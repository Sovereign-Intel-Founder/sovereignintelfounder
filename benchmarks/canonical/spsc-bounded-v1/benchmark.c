#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <stdatomic.h>

#define RING_BUFFER_SIZE 1048576
#define TOTAL_EVENTS 10000000

typedef struct {
    uint64_t buffer[RING_BUFFER_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} spsc_ring_t;

static spsc_ring_t ring = {0};

int main() {
    struct timespec start, end;
    
    printf("[*] Starting real compiled SPSC ring buffer benchmark (%d events)...\n", TOTAL_EVENTS);
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (uint64_t i = 0; i < TOTAL_EVENTS; i++) {
        size_t tail = atomic_load_explicit(&ring.tail, memory_order_relaxed);
        while (((tail + 1) & (RING_BUFFER_SIZE - 1)) == atomic_load_explicit(&ring.head, memory_order_acquire)) {
        }
        ring.buffer[tail] = i;
        atomic_store_explicit(&ring.tail, (tail + 1) & (RING_BUFFER_SIZE - 1), memory_order_release);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    
    double elapsed_sec = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    double throughput = TOTAL_EVENTS / elapsed_sec;
    double latency_ns = (elapsed_sec / TOTAL_EVENTS) * 1e9;

    printf("[+] Benchmark complete: %.2f events/sec, avg latency: %.2f ns\n", throughput, latency_ns);
    
    FILE *f = fopen("result_data.json", "w");
    if (f) {
        fprintf(f, "{\"benchmark_id\": \"spsc-bounded-v1\", \"workload_type\": \"real_compiled_c\", \"metrics\": {\"events_processed\": %d, \"throughput_eps\": %.2f, \"avg_latency_ns\": %.2f}}\n", TOTAL_EVENTS, throughput, latency_ns);
        fclose(f);
    }

    return 0;
}
