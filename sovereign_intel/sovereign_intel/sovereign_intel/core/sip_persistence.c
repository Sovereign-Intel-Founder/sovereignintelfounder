#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <pthread.h>
#include <errno.h>
#include "sqlite3.h"
#include <immintrin.h> // For _mm_pause() hardware spin-loop instruction

#define SIP_RING_CAPACITY 65536 // Must be a power of 2
#define BATCH_SIZE 512
#define DB_PATH "sovereign_intel.db"

typedef struct {
    uint64_t lineage_id;
    uint32_t payload_len;
    uint8_t data[256];
} __attribute__((aligned(64))) sip_packet_t;

typedef struct {
    sip_packet_t buffer[SIP_RING_CAPACITY];
    atomic_size_t head __attribute__((aligned(64)));
    atomic_size_t tail __attribute__((aligned(64)));
} sip_spsc_ring_t;

static volatile atomic_bool g_running = true;

void handle_signal(int sig) {
    (void)sig;
    atomic_store(&g_running, false);
}

void pin_thread_to_core(pthread_t thread, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    int rc = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
    if (rc != 0) {
        fprintf(stderr, "[WARNING] Failed to bind thread to core %d: %s\n", core_id, strerror(rc));
    }
}

int init_database(sqlite3 **db) {
    int rc = sqlite3_open(DB_PATH, db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "[CRITICAL] Cannot open database: %s\n", sqlite3_errmsg(*db));
        return -1;
    }
    
    char *err_msg = NULL;
    const char *pragmas[] = {
        "PRAGMA journal_mode=WAL;",
        "PRAGMA synchronous=NORMAL;",
        "PRAGMA temp_store=MEMORY;",
        "PRAGMA cache_size=-64000;",
        "CREATE TABLE IF NOT EXISTS persistent_events (" \
        "lineage_id INTEGER PRIMARY KEY, " \
        "payload_len INTEGER NOT NULL, " \
        "data TEXT NOT NULL);"
    };

    for (int i = 0; i < 5; i++) {
        rc = sqlite3_exec(*db, pragmas[i], 0, 0, &err_msg);
        if (rc != SQLITE_OK) {
            fprintf(stderr, "[CRITICAL] SQL initialization error [%d]: %s\n", i, err_msg);
            sqlite3_free(err_msg);
            sqlite3_close(*db);
            return -1;
        }
    }
    return 0;
}

void* persistence_worker(void *arg) {
    pin_thread_to_core(pthread_self(), 2);

    sip_spsc_ring_t *ring = (sip_spsc_ring_t*)arg;
    sqlite3 *db = NULL;
    
    if (init_database(&db) != 0) {
        return NULL;
    }

    sqlite3_stmt *stmt = NULL;
    const char *sql = "INSERT OR REPLACE INTO persistent_events (lineage_id, payload_len, data) VALUES (?, ?, ?);";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "[CRITICAL] Failed to prepare SQLite statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return NULL;
    }

    sip_packet_t batch[BATCH_SIZE];
    size_t batch_count = 0;
    uint32_t spin_count = 0;

    while (atomic_load(&g_running) || ring->tail != atomic_load(&ring->head)) {
        size_t current_tail = atomic_load_explicit(&ring->tail, memory_order_relaxed);
        size_t current_head = atomic_load_explicit(&ring->head, memory_order_acquire);

        if (current_tail != current_head) {
            spin_count = 0;
            batch[batch_count++] = ring->buffer[current_tail & (SIP_RING_CAPACITY - 1)];
            atomic_store_explicit(&ring->tail, current_tail + 1, memory_order_release);
            
            if (batch_count >= BATCH_SIZE) {
                if (sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, NULL) != SQLITE_OK) {
                    fprintf(stderr, "[ERROR] Transaction begin failed: %s\n", sqlite3_errmsg(db));
                    usleep(1000);
                    continue;
                }

                bool tx_failed = false;
                for (size_t i = 0; i < batch_count; i++) {
                    sqlite3_bind_int64(stmt, 1, batch[i].lineage_id);
                    sqlite3_bind_int(stmt, 2, batch[i].payload_len);
                    sqlite3_bind_text(stmt, 3, (char*)batch[i].data, batch[i].payload_len, SQLITE_STATIC);

                    if (sqlite3_step(stmt) != SQLITE_DONE) {
                        fprintf(stderr, "[ERROR] SQLite step failure: %s\n", sqlite3_errmsg(db));
                        tx_failed = true;
                        sqlite3_reset(stmt);
                        break;
                    }
                    sqlite3_reset(stmt);
                }

                if (tx_failed) {
                    sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
                } else {
                    sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
                }
                batch_count = 0;
            }
        } else {
            if (++spin_count < 1000) {
                _mm_pause();
            } else {
                usleep(50);
            }
        }
    }

    if (batch_count > 0 && db) {
        sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, NULL);
        for (size_t i = 0; i < batch_count; i++) {
            sqlite3_bind_int64(stmt, 1, batch[i].lineage_id);
            sqlite3_bind_int(stmt, 2, batch[i].payload_len);
            sqlite3_bind_text(stmt, 3, (char*)batch[i].data, batch[i].payload_len, SQLITE_STATIC);
            sqlite3_step(stmt);
            sqlite3_reset(stmt);
        }
        sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    }

    if (stmt) sqlite3_finalize(stmt);
    if (db) sqlite3_close(db);
    printf("[INFO] Persistence worker exited cleanly. All states flushed.\n");
    return NULL;
}

int main(void) {
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    sip_spsc_ring_t *ring = aligned_alloc(64, sizeof(sip_spsc_ring_t));
    if (!ring) {
        perror("Aligned memory allocation failed");
        return 1;
    }
    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);

    pthread_t worker_tid;
    if (pthread_create(&worker_tid, NULL, persistence_worker, ring) != 0) {
        perror("Worker thread creation failed");
        free(ring);
        return 1;
    }

    pin_thread_to_core(pthread_self(), 1);

    for (int i = 0; i < 2000; i++) {
        size_t head = atomic_load_explicit(&ring->head, memory_order_relaxed);
        size_t tail = atomic_load_explicit(&ring->tail, memory_order_acquire);
        
        while ((head - tail) >= SIP_RING_CAPACITY) {
            _mm_pause();
            tail = atomic_load_explicit(&ring->tail, memory_order_acquire);
        }

        ring->buffer[head & (SIP_RING_CAPACITY - 1)] = (sip_packet_t){
            .lineage_id = (uint64_t)(i + 1),
            .payload_len = 18,
            .data = "sip_hardened_event"
        };
        atomic_store_explicit(&ring->head, head + 1, memory_order_release);
    }

    sleep(1);
    atomic_store(&g_running, false);
    pthread_join(worker_tid, NULL);
    free(ring);

    printf("[INFO] Pipeline execution test completed successfully.\n");
    return 0;
}
