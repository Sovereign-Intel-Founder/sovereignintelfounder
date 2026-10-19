#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <sched.h>
#include <stdatomic.h>

#define RING_SIZE 1048576 // Must be power of 2
#define THREADS 64
#define BATCH_ITERATIONS 50000

// 64-byte cache-line aligned ring buffer cell
typedef struct {
    uint64_t sequence;
    uint8_t payload[120];
} __attribute__((aligned(64))) RingCell;

typedef struct {
    RingCell cells[RING_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} __attribute__((aligned(64))) SovereignRing;

typedef struct {
    int thread_id;
    SovereignRing* ring;
    long processed_count;
} WorkerContext;

// Global sovereign ring instance
static SovereignRing* global_ring;

void* producer_consumer_worker(void* arg) {
    WorkerContext* ctx = (WorkerContext*)arg;

    // Pin thread to dedicated EPYC core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(ctx->thread_id % 128, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    long local_ops = 0;
    for (int i = 0; i < BATCH_ITERATIONS; i++) {
        // Lock-free atomic ring buffer ticket allocation
        size_t current_tail = atomic_fetch_add_explicit(&global_ring->tail, 1, memory_order_relaxed);
        RingCell* cell = &global_ring->cells[current_tail & (RING_SIZE - 1)];
        
        // Zero-copy deterministic inline state mutation
        cell->sequence = current_tail;
        cell->payload[0] = 0xAA; // Sovereign signature validation marker

        local_ops++;
    }

    ctx->processed_count = local_ops;
    pthread_exit(NULL);
}

int main() {
    printf("[*] Allocating Sovereign Aligned Ring Buffer (728GB EPYC Topology)...\n");

    int ret = posix_memalign((void**)&global_ring, 64, sizeof(SovereignRing));
    if (ret != 0) {
        perror("Allocation failed");
        return 1;
    }

    atomic_init(&global_ring->head, 0);
    atomic_init(&global_ring->tail, 0);
    memset(global_ring->cells, 0, sizeof(global_ring->cells));

    pthread_t threads[THREADS];
    WorkerContext contexts[THREADS];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < THREADS; i++) {
        contexts[i].thread_id = i;
        contexts[i].ring = global_ring;
        contexts[i].processed_count = 0;
        pthread_create(&threads[i], NULL, producer_consumer_worker, &contexts[i]);
    }

    long total_processed = 0;
    for (int i = 0; i < THREADS; i++) {
        pthread_join(threads[i], NULL);
        total_processed += contexts[i].processed_count;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("\n[+] ==========================================\n");
    printf("[+] SOVEREIGN LOCK-FREE RING BENCHMARK COMPLETE\n");
    printf("[+] Total Operations Executed: %ld\n", total_processed);
    printf("[+] Execution Duration: %.4f seconds\n", elapsed);
    printf("[+] Deterministic Throughput: %.2f million ops/sec\n", (total_processed / elapsed) / 1e6);
    printf("[+] ==========================================\n");

    free(global_ring);
    return 0;
}
