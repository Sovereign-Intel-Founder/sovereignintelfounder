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
#include <sys/time.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdatomic.h>
#include <assert.h>

#ifndef CLOCK_MONOTRONIC
#define CLOCK_MONOTRONIC 1
#endif

#ifndef CLOCK_MONOTRONIC_RAW
#define CLOCK_MONOTRONIC_RAW 4
#endif

#define NUM_THREADS 128
#define EVENTS_PER_THREAD 100000
#define TOTAL_EVENTS ((uint64_t)NUM_THREADS * EVENTS_PER_THREAD)
#define SHM_NAME "/sip_native_shm_buffer"
#define RING_CAPACITY 16777216 // 2^24 ring capacity to hold all 12.8M events without drops

typedef struct {
    uint64_t sequence;
    uint64_t timestamp_ns;
    uint32_t thread_id;
    uint32_t operation_type;
    char event_id[32];
    char payload[64];
} __attribute__((packed)) sip_event_t;

typedef struct {
    _Atomic uint64_t head;
    _Atomic uint64_t tail;
    _Atomic uint64_t qsize;
    sip_event_t ring[RING_CAPACITY];
} sip_shm_ring_t;

typedef struct {
    uint32_t thread_id;
    uint32_t total_cores;
    uint64_t submitted;
    uint64_t completed;
    uint64_t failed;
    uint64_t *latencies_ns;
} thread_worker_args_t;

typedef struct {
    uint64_t latency_ns;
    uint32_t thread_id;
    uint64_t sequence;
} latency_outlier_t;

static pthread_barrier_t start_barrier;
static sip_shm_ring_t *g_shm_ring = NULL;
static _Atomic uint64_t g_submit_start_ns = 0;
static _Atomic uint64_t g_submit_end_ns = 0;

static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTRONIC_RAW, &ts) != 0) {
        clock_gettime(CLOCK_MONOTRONIC, &ts);
    }
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + (uint64_t)ts.tv_nsec;
}

static inline bool enqueue_shm_event(sip_shm_ring_t *ring, const sip_event_t *ev) {
    uint64_t current_q = atomic_load_explicit(&ring->qsize, memory_order_relaxed);
    if (current_q >= RING_CAPACITY) {
        return false;
    }

    uint64_t pos = atomic_fetch_add_explicit(&ring->head, 1, memory_order_relaxed);
    uint64_t idx = pos & (RING_CAPACITY - 1);

    memcpy((void*)&ring->ring[idx], ev, sizeof(sip_event_t));
    atomic_fetch_add_explicit(&ring->qsize, 1, memory_order_release);
    return true;
}

void* worker_thread(void *arg) {
    thread_worker_args_t *args = (thread_worker_args_t*)arg;

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(args->thread_id % args->total_cores, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    sip_event_t event;
    event.thread_id = args->thread_id;
    memset(event.payload, 0, sizeof(event.payload));
    strncpy(event.payload, "synthetic_native_workload_payload", sizeof(event.payload) - 1);

    pthread_barrier_wait(&start_barrier);

    uint64_t thread_start = get_time_ns();
    if (args->thread_id == 0) {
        atomic_store(&g_submit_start_ns, thread_start);
    }

    for (uint64_t seq = 0; seq < EVENTS_PER_THREAD; seq++) {
        event.sequence = seq;
        event.operation_type = (seq % 2 == 0) ? 0 : 1;
        snprintf(event.event_id, sizeof(event.event_id), "native-%u-%lu", args->thread_id, seq);

        uint64_t t0 = get_time_ns();
        event.timestamp_ns = t0;

        bool ok = enqueue_shm_event(g_shm_ring, &event);

        uint64_t t1 = get_time_ns();
        uint64_t elapsed_ns = t1 - t0;

        args->submitted++;
        if (ok) {
            args->completed++;
        } else {
            args->failed++;
        }
        args->latencies_ns[seq] = elapsed_ns;
    }

    uint64_t thread_end = get_time_ns();
    uint64_t current_max = atomic_load(&g_submit_end_ns);
    while (thread_end > current_max && !atomic_compare_exchange_weak(&g_submit_end_ns, &current_max, thread_end));

    return NULL;
}

static int compare_uint64(const void *a, const void *b) {
    uint64_t arg1 = *(const uint64_t*)a;
    uint64_t arg2 = *(const uint64_t*)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

static int compare_outliers(const void *a, const void *b) {
    const latency_outlier_t *o1 = (const latency_outlier_t*)a;
    const latency_outlier_t *o2 = (const latency_outlier_t*)b;
    if (o1->latency_ns > o2->latency_ns) return -1;
    if (o1->latency_ns < o2->latency_ns) return 1;
    return 0;
}

int main(void) {
    long num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (num_cores <= 0) num_cores = 128;

    shm_unlink(SHM_NAME);
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open failed");
        return 1;
    }
    if (ftruncate(shm_fd, sizeof(sip_shm_ring_t)) == -1) {
        perror("ftruncate failed");
        return 1;
    }

    g_shm_ring = (sip_shm_ring_t*)mmap(NULL, sizeof(sip_shm_ring_t), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (g_shm_ring == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    memset(g_shm_ring, 0, sizeof(sip_shm_ring_t));

    pthread_t threads[NUM_THREADS];
    thread_worker_args_t args[NUM_THREADS];
    pthread_barrier_init(&start_barrier, NULL, NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].thread_id = i;
        args[i].total_cores = (uint32_t)num_cores;
        args[i].submitted = 0;
        args[i].completed = 0;
        args[i].failed = 0;
        args[i].latencies_ns = (uint64_t*)malloc(EVENTS_PER_THREAD * sizeof(uint64_t));
        if (!args[i].latencies_ns) {
            fprintf(stderr, "Failed memory allocation for thread %d\n", i);
            return 1;
        }
    }

    uint64_t global_start_ns = get_time_ns();

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, worker_thread, &args[i]);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    uint64_t global_end_ns = get_time_ns();

    uint64_t total_submitted = 0;
    uint64_t total_completed = 0;
    uint64_t total_failed = 0;

    uint64_t *all_latencies = (uint64_t*)malloc(TOTAL_EVENTS * sizeof(uint64_t));
    latency_outlier_t *outliers = (latency_outlier_t*)malloc(TOTAL_EVENTS * sizeof(latency_outlier_t));

    if (!all_latencies || !outliers) {
        fprintf(stderr, "Failed memory allocation for latency aggregations\n");
        return 1;
    }

    uint64_t flat_idx = 0;
    for (int i = 0; i < NUM_THREADS; i++) {
        total_submitted += args[i].submitted;
        total_completed += args[i].completed;
        total_failed += args[i].failed;

        for (uint64_t seq = 0; seq < EVENTS_PER_THREAD; seq++) {
            uint64_t lat = args[i].latencies_ns[seq];
            all_latencies[flat_idx] = lat;
            outliers[flat_idx].latency_ns = lat;
            outliers[flat_idx].thread_id = i;
            outliers[flat_idx].sequence = seq;
            flat_idx++;
        }
        free(args[i].latencies_ns);
    }

    // Consistency Assertions
    assert(total_submitted == 12800000ULL);
    assert(total_completed == 12800000ULL);
    assert(total_failed == 0ULL);

    qsort(all_latencies, TOTAL_EVENTS, sizeof(uint64_t), compare_uint64);
    qsort(outliers, TOTAL_EVENTS, sizeof(latency_outlier_t), compare_outliers);

    double global_wall_sec = (double)(global_end_ns - global_start_ns) / 1e9;
    double submit_window_sec = (double)(atomic_load(&g_submit_end_ns) - atomic_load(&g_submit_start_ns)) / 1e9;

    double global_wall_throughput = (double)total_completed / global_wall_sec;
    double submit_throughput = (double)total_submitted / submit_window_sec;

    printf("{\n");
    printf("  \"NATIVE DIAGNOSTIC RESULT — REQUIRES TIMING-BOUNDARY AUDIT\": {\n");
    printf("    \"architecture\": \"Bare-Metal C11 POSIX SHM Ring Producer Harness\",\n");
    printf("    \"threads\": %d,\n", NUM_THREADS);
    printf("    \"events_per_thread\": %d,\n", EVENTS_PER_THREAD);
    printf("    \"total_submitted\": %lu,\n", total_submitted);
    printf("    \"total_completed\": %lu,\n", total_completed);
    printf("    \"total_failed\": %lu,\n", total_failed);
    printf("    \"timing_boundaries\": {\n");
    printf("      \"global_wall_clock_sec\": %.6f,\n", global_wall_sec);
    printf("      \"submission_window_sec\": %.6f\n", submit_window_sec);
    printf("    },\n");
    printf("    \"throughput_metrics\": {\n");
    printf("      \"GLOBAL WALL-CLOCK THROUGHPUT (total_completed / global_wall_sec)\": %.2f,\n", global_wall_throughput);
    printf("      \"SUBMISSION-PHASE THROUGHPUT (total_submitted / submission_window_sec)\": %.2f\n", submit_throughput);
    printf("    },\n");
    printf("    \"enqueue_tail_latencies_ms\": {\n");
    printf("      \"min\": %.6f,\n", (double)all_latencies[0] / 1e6);
    printf("      \"p50\": %.6f,\n", (double)all_latencies[(uint64_t)(TOTAL_EVENTS * 0.50)] / 1e6);
    printf("      \"p95\": %.6f,\n", (double)all_latencies[(uint64_t)(TOTAL_EVENTS * 0.95)] / 1e6);
    printf("      \"p99\": %.6f,\n", (double)all_latencies[(uint64_t)(TOTAL_EVENTS * 0.99)] / 1e6);
    printf("      \"p999\": %.6f,\n", (double)all_latencies[(uint64_t)(TOTAL_EVENTS * 0.999)] / 1e6);
    printf("      \"max\": %.6f\n", (double)all_latencies[TOTAL_EVENTS - 1] / 1e6);
    printf("    }\n");
    printf("  }\n");
    printf("}\n");

    free(all_latencies);
    free(outliers);
    pthread_barrier_destroy(&start_barrier);
    munmap(g_shm_ring, sizeof(sip_shm_ring_t));
    close(shm_fd);
    shm_unlink(SHM_NAME);

    return 0;
}
