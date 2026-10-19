#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdatomic.h>

#define WINDOW_SIZE 65536
#define TOTAL_ITERATIONS 5000000

typedef struct {
    uint64_t samples[WINDOW_SIZE];
    atomic_size_t head;
} entropy_ring_t;

static entropy_ring_t ring = {0};

static inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

int main() {
    printf("[*] Initializing Predictive Entropy Horizon Engine (Window: %d, Iterations: %d)...\n", WINDOW_SIZE, TOTAL_ITERATIONS);
    
    uint64_t start_cycles = rdtsc();
    struct timespec start_t, end_t;
    clock_gettime(CLOCK_MONOTONIC, &start_t);

    double rolling_entropy = 0.0;
    uint64_t anomalies_detected = 0;

    for (uint64_t i = 0; i < TOTAL_ITERATIONS; i++) {
        uint64_t val = i ^ (i >> 3);
        size_t pos = atomic_fetch_add_explicit(&ring.head, 1, memory_order_relaxed) & (WINDOW_SIZE - 1);
        ring.samples[pos] = val;

        if (i % 1000 == 0) {
            double p = (double)(val & 0xFF) / 255.0;
            if (p > 0.0 && p < 1.0) {
                rolling_entropy = -(p * log2(p) + (1.0 - p) * log2(1.0 - p));
            }
            if (rolling_entropy > 0.95) {
                anomalies_detected++;
            }
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end_t);
    uint64_t end_cycles = rdtsc();

    double elapsed_sec = (end_t.tv_sec - start_t.tv_sec) + (end_t.tv_nsec - start_t.tv_nsec) / 1e9;
    double cycles_per_op = (double)(end_cycles - start_cycles) / TOTAL_ITERATIONS;

    printf("[+] Predictive Engine Complete: cycles/op=%.2f, anomalies_flagged=%lu, duration=%.4fs\n", cycles_per_op, anomalies_detected, elapsed_sec);

    FILE *f = fopen("result_data.json", "w");
    if (f) {
        fprintf(f, "{\"benchmark_id\": \"predictive-entropy-horizon-v1\", \"workload_type\": \"real_compiled_c_predictive\", \"metrics\": {\"iterations\": %d, \"cycles_per_operation\": %.2f, \"anomalies_resurrected\": %lu, \"execution_time_sec\": %.4f}}\n", TOTAL_ITERATIONS, cycles_per_op, anomalies_detected, elapsed_sec);
        fclose(f);
    }

    return 0;
}
