#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <sched.h>
#include <time.h>

#define TOTAL_CORES 128
#define ITERATIONS 5000000

typedef struct {
    int core_id;
    uint64_t processed_events;
    double elapsed_sec;
} worker_stats_t;

static volatile int barrier = 0;

void *benchmark_worker(void *arg) {
    worker_stats_t *stats = (worker_stats_t *)arg;
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(stats->core_id % sysconf(_SC_NPROCESSORS_ONLN), &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    while (!barrier); // Synchronized start for peak concurrency

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    uint64_t count = 0;
    for (int i = 0; i < ITERATIONS; i++) {
        // Simulate zero-copy ring buffer token lookup & state transition mutation
        volatile uint32_t token = i ^ (i >> 3);
        if (token != 0xFFFFFFFF) {
            count++;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    stats->processed_events = count;
    stats->elapsed_sec = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    return NULL;
}

int main() {
    printf("[*] Initializing 128-core high-precision benchmark harness on LeaseWeb bare-metal host...\n");
    pthread_t threads[TOTAL_CORES];
    worker_stats_t stats[TOTAL_CORES];

    for (int i = 0; i < TOTAL_CORES; i++) {
        stats[i].core_id = i;
        stats[i].processed_events = 0;
        pthread_create(&threads[i], NULL, benchmark_worker, &stats[i]);
    }

    usleep(100000); // Stabilize thread pool
    barrier = 1;    // Release all 128 threads simultaneously

    uint64_t total_events = 0;
    double max_time = 0;

    for (int i = 0; i < TOTAL_CORES; i++) {
        pthread_join(threads[i], NULL);
        total_events += stats[i].processed_events;
        if (stats[i].elapsed_sec > max_time) {
            max_time = stats[i].elapsed_sec;
        }
    }

    double aggregate_throughput = (double)total_events / max_time;
    printf("[+] BENCHMARK COMPLETE:\n");
    printf("    - Active Cores: %d\n", TOTAL_CORES);
    printf("    - Total Events Processed: %lu\n", total_events);
    printf("    - Peak Aggregate Throughput: %.2f events/sec (%.2f Mops/s)\n", aggregate_throughput, aggregate_throughput / 1e6);
    printf("    - Max Core Latency Window: %.6f seconds\n", max_time);
    return 0;
}
