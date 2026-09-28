#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE
#ifndef CLOCK_MONOTRONIC
#define CLOCK_MONOTRONIC 1
#endif
#ifndef CLOCK_MONOTRONIC_RAW
#define CLOCK_MONOTRONIC_RAW 4
#endif
#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdatomic.h>
#include <assert.h>

#ifndef RING_CAPACITY
#define RING_CAPACITY 64ULL
#endif

#ifndef TOTAL_EVENTS
#define TOTAL_EVENTS 10000ULL
#endif

#define SHM_NAME "/sip_spsc_shm_buffer"

typedef struct {
    uint64_t sequence;
    uint64_t timestamp_ns;
    uint32_t thread_id;
    uint32_t operation_type;
    uint32_t checksum;
    char event_id[32];
    char payload[64];
} __attribute__((packed)) sip_event_t;

typedef struct {
    _Atomic uint64_t head;
    _Atomic uint64_t tail;
    sip_event_t ring[RING_CAPACITY];
} sip_shm_ring_t;

static sip_shm_ring_t *g_shm_ring = NULL;

static _Atomic uint64_t g_submitted = 0;
static _Atomic uint64_t g_enqueued = 0;
static _Atomic uint64_t g_dequeued = 0;
static _Atomic uint64_t g_validated = 0;
static _Atomic uint64_t g_completed = 0;
static _Atomic uint64_t g_failed = 0;
static _Atomic uint64_t g_dropped = 0;

static _Atomic uint64_t g_duplicates = 0;
static _Atomic uint64_t g_missing = 0;
static _Atomic uint64_t g_out_of_order = 0;
static _Atomic uint64_t g_checksum_mismatches = 0;

static _Atomic uint64_t g_queue_full_obs = 0;
static _Atomic uint64_t g_queue_empty_obs = 0;
static _Atomic uint64_t g_producer_spins = 0;
static _Atomic uint64_t g_consumer_spins = 0;

static _Atomic uint64_t g_max_qsize = 0;
static _Atomic uint64_t g_wraparound_count = 0;

static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTRONIC_RAW, &ts) != 0) {
        clock_gettime(CLOCK_MONOTRONIC, &ts);
    }
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + (uint64_t)ts.tv_nsec;
}

static inline uint32_t compute_checksum(const sip_event_t *ev) {
    uint32_t cs = 0;
    const uint8_t *p = (const uint8_t*)ev->payload;
    for (size_t i = 0; i < sizeof(ev->payload); i++) {
        cs = (cs * 31) + p[i];
    }
    return cs ^ (uint32_t)ev->sequence;
}

void* producer_thread(void *arg) {
    (void)arg;
    for (uint64_t seq = 0; seq < TOTAL_EVENTS; seq++) {
        sip_event_t ev;
        ev.sequence = seq;
        ev.timestamp_ns = get_time_ns();
        ev.thread_id = 0;
        ev.operation_type = (seq % 2 == 0) ? 0 : 1;
        snprintf(ev.event_id, sizeof(ev.event_id), "spsc-prod-%lu", seq);
        memset(ev.payload, 'A' + (seq % 26), sizeof(ev.payload) - 1);
        ev.payload[sizeof(ev.payload) - 1] = '\0';
        ev.checksum = compute_checksum(&ev);

        atomic_fetch_add_explicit(&g_submitted, 1, memory_order_relaxed);

        while (1) {
            uint64_t h = atomic_load_explicit(&g_shm_ring->head, memory_order_relaxed);
            uint64_t t = atomic_load_explicit(&g_shm_ring->tail, memory_order_acquire);
            uint64_t qsize = h - t;

            if (qsize > atomic_load_explicit(&g_max_qsize, memory_order_relaxed)) {
                atomic_store_explicit(&g_max_qsize, qsize, memory_order_relaxed);
            }

            if (qsize >= RING_CAPACITY) {
                atomic_fetch_add_explicit(&g_queue_full_obs, 1, memory_order_relaxed);
                atomic_fetch_add_explicit(&g_producer_spins, 1, memory_order_relaxed);
                sched_yield();
                continue;
            }

            uint64_t idx = h & (RING_CAPACITY - 1);
            if (idx == 0 && h > 0) {
                atomic_fetch_add_explicit(&g_wraparound_count, 1, memory_order_relaxed);
            }

            g_shm_ring->ring[idx] = ev;
            atomic_store_explicit(&g_shm_ring->head, h + 1, memory_order_release);
            atomic_fetch_add_explicit(&g_enqueued, 1, memory_order_relaxed);
            break;
        }
    }
    return NULL;
}

void* consumer_thread(void *arg) {
    (void)arg;
    uint64_t expected_seq = 0;

    while (expected_seq < TOTAL_EVENTS) {
        uint64_t t = atomic_load_explicit(&g_shm_ring->tail, memory_order_relaxed);
        uint64_t h = atomic_load_explicit(&g_shm_ring->head, memory_order_acquire);

        if (t == h) {
            atomic_fetch_add_explicit(&g_queue_empty_obs, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&g_consumer_spins, 1, memory_order_relaxed);
            sched_yield();
            continue;
        }

        uint64_t idx = t & (RING_CAPACITY - 1);
        sip_event_t ev = g_shm_ring->ring[idx];
        atomic_store_explicit(&g_shm_ring->tail, t + 1, memory_order_release);

        atomic_fetch_add_explicit(&g_dequeued, 1, memory_order_relaxed);

        if (compute_checksum(&ev) != ev.checksum) {
            atomic_fetch_add_explicit(&g_checksum_mismatches, 1, memory_order_relaxed);
        }

        if (ev.sequence == expected_seq) {
            atomic_fetch_add_explicit(&g_validated, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&g_completed, 1, memory_order_relaxed);
        } else if (ev.sequence < expected_seq) {
            atomic_fetch_add_explicit(&g_duplicates, 1, memory_order_relaxed);
        } else {
            atomic_fetch_add_explicit(&g_missing, ev.sequence - expected_seq, memory_order_relaxed);
            atomic_fetch_add_explicit(&g_out_of_order, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&g_validated, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&g_completed, 1, memory_order_relaxed);
            expected_seq = ev.sequence;
        }
        expected_seq++;
    }
    return NULL;
}

int main(void) {
    shm_unlink(SHM_NAME);
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) { perror("shm_open"); return 1; }
    if (ftruncate(shm_fd, sizeof(sip_shm_ring_t)) == -1) { perror("ftruncate"); return 1; }

    g_shm_ring = (sip_shm_ring_t*)mmap(NULL, sizeof(sip_shm_ring_t), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (g_shm_ring == MAP_FAILED) { perror("mmap"); return 1; }
    memset(g_shm_ring, 0, sizeof(sip_shm_ring_t));

    pthread_t prod_t, cons_t;
    uint64_t t0 = get_time_ns();

    pthread_create(&prod_t, NULL, producer_thread, NULL);
    pthread_create(&cons_t, NULL, consumer_thread, NULL);

    pthread_join(prod_t, NULL);
    pthread_join(cons_t, NULL);

    uint64_t t1 = get_time_ns();
    double elapsed_sec = (double)(t1 - t0) / 1e9;

    uint64_t sub = atomic_load(&g_submitted);
    uint64_t enq = atomic_load(&g_enqueued);
    uint64_t deq = atomic_load(&g_dequeued);
    uint64_t val = atomic_load(&g_validated);
    uint64_t cmp = atomic_load(&g_completed);
    uint64_t fail = atomic_load(&g_failed);
    uint64_t drop = atomic_load(&g_dropped);

    uint64_t dup = atomic_load(&g_duplicates);
    uint64_t miss = atomic_load(&g_missing);
    uint64_t ooo = atomic_load(&g_out_of_order);
    uint64_t cs_err = atomic_load(&g_checksum_mismatches);

    uint64_t final_head = atomic_load(&g_shm_ring->head);
    uint64_t final_tail = atomic_load(&g_shm_ring->tail);
    uint64_t final_qsize = final_head - final_tail;

    printf("====================================================\n");
    printf("NATIVE SIP SPSC BOUNDED-RING WRAPAROUND BENCHMARK\n");
    printf("====================================================\n");
    printf("Config: RING_CAPACITY=%llu, TOTAL_EVENTS=%llu\n", (unsigned long long)RING_CAPACITY, (unsigned long long)TOTAL_EVENTS);
    printf("Elapsed Time: %.6f sec (Throughput: %.2f ops/sec)\n", elapsed_sec, (double)cmp / elapsed_sec);
    printf("Submitted: %lu, Enqueued: %lu, Dequeued: %lu, Validated: %lu, Completed: %lu, Failed: %lu, Dropped: %lu\n",
           sub, enq, deq, val, cmp, fail, drop);
    printf("Integrity: Duplicates=%lu, Missing=%lu, OutOfOrder=%lu, ChecksumErrors=%lu\n",
           dup, miss, ooo, cs_err);
    printf("Queue State: FinalHead=%lu, FinalTail=%lu, FinalQSize=%lu, MaxQSize=%lu, WraparoundCount=%lu\n",
           final_head, final_tail, final_qsize, atomic_load(&g_max_qsize), atomic_load(&g_wraparound_count));
    printf("Observations: QueueFullObs=%lu, QueueEmptyObs=%lu, ProducerSpins=%lu, ConsumerSpins=%lu\n",
           atomic_load(&g_queue_full_obs), atomic_load(&g_queue_empty_obs),
           atomic_load(&g_producer_spins), atomic_load(&g_consumer_spins));

    assert(sub == enq + fail);
    assert(enq == deq);
    assert(deq == val);
    assert(val == cmp);
    assert(drop == 0);
    assert(dup == 0);
    assert(miss == 0);
    assert(ooo == 0);
    assert(cs_err == 0);
    assert(final_qsize == 0);
    assert(atomic_load(&g_wraparound_count) > 0);

    printf("\nALL AUDIT ASSERTIONS PASSED SUCCESSFULLY.\n");

    munmap(g_shm_ring, sizeof(sip_shm_ring_t));
    close(shm_fd);
    shm_unlink(SHM_NAME);
    return 0;
}
