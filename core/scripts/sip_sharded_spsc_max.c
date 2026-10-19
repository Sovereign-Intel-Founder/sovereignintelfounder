#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#ifndef CLOCK_MONOTRONIC
#define CLOCK_MONOTRONIC 1
#endif
#ifndef CLOCK_MONOTRONIC_RAW
#define CLOCK_MONOTRONIC_RAW 4
#endif

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>
#include <sched.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdatomic.h>
#include <assert.h>

#define MAX_LANES 128
#define SAMPLE_MAX 100000

typedef struct {
    uint64_t sequence;
    uint64_t enqueue_ts_ns;
    uint32_t lane_id;
    uint32_t operation_type;
    uint32_t checksum;
    char event_id[32];
    char payload[64];
} __attribute__((packed)) sip_event_t;

typedef struct {
    _Atomic uint64_t head;
    _Atomic uint64_t tail;
    sip_event_t *ring;
    uint64_t capacity;
    
    // Lane metrics
    _Atomic uint64_t submitted;
    _Atomic uint64_t enqueued;
    _Atomic uint64_t dequeued;
    _Atomic uint64_t validated;
    _Atomic uint64_t completed;
    _Atomic uint64_t failed;
    _Atomic uint64_t dropped;

    _Atomic uint64_t duplicates;
    _Atomic uint64_t missing;
    _Atomic uint64_t out_of_order;
    _Atomic uint64_t checksum_mismatches;

    _Atomic uint64_t queue_full_obs;
    _Atomic uint64_t queue_empty_obs;
    _Atomic uint64_t producer_spins;
    _Atomic uint64_t consumer_spins;

    _Atomic uint64_t max_qsize;
    _Atomic uint64_t wraparound_count;

    // Bounded latency samples
    uint64_t sample_count;
    uint64_t enqueue_latencies[SAMPLE_MAX];
    uint64_t e2e_latencies[SAMPLE_MAX];
    uint64_t consumer_latencies[SAMPLE_MAX];
} lane_context_t;

typedef struct {
    uint32_t lane_id;
    uint64_t total_events;
    lane_context_t *lane;
} thread_arg_t;

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

static int compare_uint64(const void *a, const void *b) {
    uint64_t arg1 = *(const uint64_t *)a;
    uint64_t arg2 = *(const uint64_t *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

static void pin_thread_to_core(pthread_t thread, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    int online_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (online_cores > 0) {
        core_id = core_id % online_cores;
    }
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
}

static uint64_t g_total_events_per_lane = 10000ULL;
static uint64_t g_ring_capacity = 4096ULL;
static uint32_t g_num_lanes = 1;

void* producer_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t*)arg;
    lane_context_t *lane = targ->lane;
    uint32_t lane_id = targ->lane_id;

    pin_thread_to_core(pthread_self(), lane_id * 2);

    for (uint64_t seq = 0; seq < targ->total_events; seq++) {
        sip_event_t ev;
        ev.sequence = seq;
        ev.lane_id = lane_id;
        ev.operation_type = (seq % 2 == 0) ? 0 : 1;
        snprintf(ev.event_id, sizeof(ev.event_id), "lane-%u-seq-%lu", lane_id, seq);
        memset(ev.payload, 'S' + (seq % 26), sizeof(ev.payload) - 1);
        ev.payload[sizeof(ev.payload) - 1] = '\0';
        ev.checksum = compute_checksum(&ev);

        atomic_fetch_add_explicit(&lane->submitted, 1, memory_order_relaxed);
        uint64_t t_start = get_time_ns();
        ev.enqueue_ts_ns = t_start;

        while (1) {
            uint64_t h = atomic_load_explicit(&lane->head, memory_order_relaxed);
            uint64_t t = atomic_load_explicit(&lane->tail, memory_order_acquire);
            uint64_t qsize = h - t;

            if (qsize > atomic_load_explicit(&lane->max_qsize, memory_order_relaxed)) {
                atomic_store_explicit(&lane->max_qsize, qsize, memory_order_relaxed);
            }

            if (qsize >= lane->capacity) {
                atomic_fetch_add_explicit(&lane->queue_full_obs, 1, memory_order_relaxed);
                atomic_fetch_add_explicit(&lane->producer_spins, 1, memory_order_relaxed);
                sched_yield();
                continue;
            }

            uint64_t idx = h & (lane->capacity - 1);
            if (idx == 0 && h > 0) {
                atomic_fetch_add_explicit(&lane->wraparound_count, 1, memory_order_relaxed);
            }

            lane->ring[idx] = ev;
            atomic_store_explicit(&lane->head, h + 1, memory_order_release);
            atomic_fetch_add_explicit(&lane->enqueued, 1, memory_order_relaxed);

            uint64_t t_end = get_time_ns();
            if (lane->sample_count < SAMPLE_MAX) {
                uint64_t s_idx = lane->sample_count++;
                lane->enqueue_latencies[s_idx] = t_end - t_start;
            }
            break;
        }
    }
    return NULL;
}

void* consumer_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t*)arg;
    lane_context_t *lane = targ->lane;
    uint32_t lane_id = targ->lane_id;

    pin_thread_to_core(pthread_self(), (lane_id * 2) + 1);

    uint64_t expected_seq = 0;
    uint64_t sample_idx = 0;

    while (expected_seq < targ->total_events) {
        uint64_t t = atomic_load_explicit(&lane->tail, memory_order_relaxed);
        uint64_t h = atomic_load_explicit(&lane->head, memory_order_acquire);

        if (t == h) {
            atomic_fetch_add_explicit(&lane->queue_empty_obs, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&lane->consumer_spins, 1, memory_order_relaxed);
            sched_yield();
            continue;
        }

        uint64_t t_cons_start = get_time_ns();
        uint64_t idx = t & (lane->capacity - 1);
        sip_event_t ev = lane->ring[idx];
        atomic_store_explicit(&lane->tail, t + 1, memory_order_release);
        uint64_t t_cons_end = get_time_ns();

        atomic_fetch_add_explicit(&lane->dequeued, 1, memory_order_relaxed);

        if (compute_checksum(&ev) != ev.checksum) {
            atomic_fetch_add_explicit(&lane->checksum_mismatches, 1, memory_order_relaxed);
        }

        if (ev.sequence == expected_seq) {
            atomic_fetch_add_explicit(&lane->validated, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&lane->completed, 1, memory_order_relaxed);
        } else if (ev.sequence < expected_seq) {
            atomic_fetch_add_explicit(&lane->duplicates, 1, memory_order_relaxed);
        } else {
            atomic_fetch_add_explicit(&lane->missing, ev.sequence - expected_seq, memory_order_relaxed);
            atomic_fetch_add_explicit(&lane->out_of_order, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&lane->validated, 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&lane->completed, 1, memory_order_relaxed);
            expected_seq = ev.sequence;
        }

        if (sample_idx < SAMPLE_MAX) {
            lane->consumer_latencies[sample_idx] = t_cons_end - t_cons_start;
            lane->e2e_latencies[sample_idx] = t_cons_end - ev.enqueue_ts_ns;
            sample_idx++;
        }

        expected_seq++;
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc > 1) g_num_lanes = atoi(argv[1]);
    if (argc > 2) g_total_events_per_lane = strtoull(argv[2], NULL, 10);
    if (argc > 3) g_ring_capacity = strtoull(argv[3], NULL, 10);

    if (g_num_lanes > MAX_LANES) g_num_lanes = MAX_LANES;

    int online_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    printf("====================================================\n");
    printf("NATIVE SIP SHARDED-SPSC AGGREGATE BENCHMARK\n");
    printf("====================================================\n");
    printf("Config: Lanes=%u, EventsPerLane=%lu, RingCapacity=%lu, OnlineCPUs=%d\n",
           g_num_lanes, g_total_events_per_lane, g_ring_capacity, online_cpus);

    lane_context_t *lanes = calloc(g_num_lanes, sizeof(lane_context_t));
    pthread_t *prod_threads = calloc(g_num_lanes, sizeof(pthread_t));
    pthread_t *cons_threads = calloc(g_num_lanes, sizeof(pthread_t));
    thread_arg_t *prod_args = calloc(g_num_lanes, sizeof(thread_arg_t));
    thread_arg_t *cons_args = calloc(g_num_lanes, sizeof(thread_arg_t));

    for (uint32_t i = 0; i < g_num_lanes; i++) {
        lanes[i].capacity = g_ring_capacity;
        lanes[i].ring = calloc(g_ring_capacity, sizeof(sip_event_t));
        atomic_init(&lanes[i].head, 0);
        atomic_init(&lanes[i].tail, 0);
    }

    uint64_t t0 = get_time_ns();

    for (uint32_t i = 0; i < g_num_lanes; i++) {
        prod_args[i].lane_id = i;
        prod_args[i].total_events = g_total_events_per_lane;
        prod_args[i].lane = &lanes[i];

        cons_args[i].lane_id = i;
        cons_args[i].total_events = g_total_events_per_lane;
        cons_args[i].lane = &lanes[i];

        pthread_create(&prod_threads[i], NULL, producer_thread, &prod_args[i]);
        pthread_create(&cons_threads[i], NULL, consumer_thread, &cons_args[i]);
    }

    for (uint32_t i = 0; i < g_num_lanes; i++) {
        pthread_join(prod_threads[i], NULL);
        pthread_join(cons_threads[i], NULL);
    }

    uint64_t t1 = get_time_ns();
    double elapsed_sec = (double)(t1 - t0) / 1e9;

    uint64_t total_submitted = 0;
    uint64_t total_enqueued = 0;
    uint64_t total_dequeued = 0;
    uint64_t total_validated = 0;
    uint64_t total_completed = 0;
    uint64_t total_failed = 0;
    uint64_t total_dropped = 0;
    uint64_t total_duplicates = 0;
    uint64_t total_missing = 0;
    uint64_t total_out_of_order = 0;
    uint64_t total_checksum_mismatches = 0;
    uint64_t total_queue_full = 0;
    uint64_t total_queue_empty = 0;
    uint64_t max_global_qsize = 0;
    uint64_t total_wraparounds = 0;

    for (uint32_t i = 0; i < g_num_lanes; i++) {
        total_submitted += atomic_load(&lanes[i].submitted);
        total_enqueued += atomic_load(&lanes[i].enqueued);
        total_dequeued += atomic_load(&lanes[i].dequeued);
        total_validated += atomic_load(&lanes[i].validated);
        total_completed += atomic_load(&lanes[i].completed);
        total_failed += atomic_load(&lanes[i].failed);
        total_dropped += atomic_load(&lanes[i].dropped);
        total_duplicates += atomic_load(&lanes[i].duplicates);
        total_missing += atomic_load(&lanes[i].missing);
        total_out_of_order += atomic_load(&lanes[i].out_of_order);
        total_checksum_mismatches += atomic_load(&lanes[i].checksum_mismatches);
        total_queue_full += atomic_load(&lanes[i].queue_full_obs);
        total_queue_empty += atomic_load(&lanes[i].queue_empty_obs);
        total_wraparounds += atomic_load(&lanes[i].wraparound_count);

        uint64_t qsz = atomic_load(&lanes[i].head) - atomic_load(&lanes[i].tail);
        if (qsz > max_global_qsize) max_global_qsize = qsz;
        assert(qsz == 0);
        assert(atomic_load(&lanes[i].wraparound_count) > 0);
    }

    double aggregate_throughput = (double)total_completed / elapsed_sec;

    printf("Elapsed Time: %.6f sec (Aggregate Throughput: %.2f ops/sec)\n", elapsed_sec, aggregate_throughput);
    printf("Accounting: Submitted=%lu, Enqueued=%lu, Dequeued=%lu, Validated=%lu, Completed=%lu, Failed=%lu, Dropped=%lu\n",
           total_submitted, total_enqueued, total_dequeued, total_validated, total_completed, total_failed, total_dropped);
    printf("Integrity: Duplicates=%lu, Missing=%lu, OutOfOrder=%lu, ChecksumErrors=%lu\n",
           total_duplicates, total_missing, total_out_of_order, total_checksum_mismatches);
    printf("Queue State: MaxQSize=%lu, WraparoundCount=%lu, QueueFullObs=%lu, QueueEmptyObs=%lu\n",
           max_global_qsize, total_wraparounds, total_queue_full, total_queue_empty);

    assert(total_submitted == total_completed + total_failed + total_dropped);
    assert(total_enqueued == total_dequeued);
    assert(total_dequeued == total_validated);
    assert(total_validated == total_completed);
    assert(total_dropped == 0);
    assert(total_duplicates == 0);
    assert(total_missing == 0);
    assert(total_out_of_order == 0);
    assert(total_checksum_mismatches == 0);

    printf("\nALL SHARDED SPSC AUDIT ASSERTIONS PASSED SUCCESSFULLY.\n");

    for (uint32_t i = 0; i < g_num_lanes; i++) {
        free(lanes[i].ring);
    }
    free(lanes);
    free(prod_threads);
    free(cons_threads);
    free(prod_args);
    free(cons_args);
    return 0;
}
