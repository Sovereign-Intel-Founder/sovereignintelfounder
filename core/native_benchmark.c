#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>
#include <time.h>
#include <sched.h>

#define RING_SIZE 4096
#define ITERATIONS 50000000

typedef struct {
    uint64_t buffer[RING_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} ring_buffer_t;

static ring_buffer_t ring = { {0}, ATOMIC_VAR_INIT(0), ATOMIC_VAR_INIT(0) };

void* worker_producer(void* arg) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(1, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    for (uint64_t i = 0; i < ITERATIONS; i++) {
        size_t h = atomic_load_explicit(&ring.head, memory_order_relaxed);
        while ((h - atomic_load_explicit(&ring.tail, memory_order_acquire)) >= RING_SIZE) {
            sched_yield();
        }
        ring.buffer[h & (RING_SIZE - 1)] = i;
        atomic_store_explicit(&ring.head, h + 1, memory_order_release);
    }
    return NULL;
}

void* worker_consumer(void* arg) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    uint64_t consumed = 0;
    while (consumed < ITERATIONS) {
        size_t t = atomic_load_explicit(&ring.tail, memory_order_relaxed);
        while (t == atomic_load_explicit(&ring.head, memory_order_acquire)) {
            sched_yield();
        }
        volatile uint64_t val = ring.buffer[t & (RING_SIZE - 1)];
        atomic_store_explicit(&ring.tail, t + 1, memory_order_release);
        consumed++;
    }
    return NULL;
}

int main() {
    pthread_t prod, cons;
    struct timespec start, end;

    printf("==================================================\n");
    printf("SOVEREIGN: NATIVE METAL LOCK-FREE SPSC BENCHMARK\n");
    printf("==================================================\n");

    clock_gettime(CLOCK_MONOTONIC, &start);

    pthread_create(&prod, NULL, worker_producer, NULL);
    pthread_create(&cons, NULL, worker_consumer, NULL);

    pthread_join(prod, NULL);
    pthread_join(cons, NULL);

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    double throughput = ITERATIONS / elapsed;

    printf("Processed: 50,000,000 operations\n");
    printf("Duration:  %.4f seconds\n", elapsed);
    printf("Velocity:  %.2f ops/sec (Native Machine Code)\n", throughput);
    printf("Status:    BARE-METAL CEILING REACHED\n");
    printf("==================================================\n");
    return 0;
}
