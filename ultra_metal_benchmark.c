#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <time.h>
#include <string.h>

#define TOTAL_OPERATIONS 100000000UL // 100 Million operations for extreme scale
#define MAX_THREADS 128

// Atomic counters and control flags
atomic_ulong global_counter = ATOMIC_VAR_INIT(0);
atomic_int keep_running = ATOMIC_VAR_INIT(1);

typedef struct {
    int thread_id;
    int num_threads;
    unsigned long ops_completed;
} worker_arg_t;

// Ultra-fast lock-free work distribution thread
void* worker_ring_simulation(void* arg) {
    worker_arg_t* warg = (worker_arg_t*)arg;
    unsigned long local_ops = 0;
    
    // Each thread grabs work atomically from the global pool
    while (1) {
        unsigned long current = atomic_fetch_add(&global_counter, 1000UL);
        if (current >= TOTAL_OPERATIONS) {
            break;
        }
        // Simulate high-speed cache-local ring buffer queue enqueues/dequeues
        for (volatile int i = 0; i < 1000; i++) {
            local_ops++;
        }
    }
    warg->ops_completed = local_ops;
    return NULL;
}

int main(int argc, char* argv[]) {
    int num_threads = MAX_THREADS;
    if (argc > 1) {
        num_threads = atoi(argv[1]);
        if (num_threads <= 0 || num_threads > MAX_THREADS) {
            num_threads = MAX_THREADS;
        }
    }

    printf("============================================================\n");
    printf("   SOVEREIGN INTELLIGENCE PROTOCOL - NATIVE C METAL ENGINE   \n");
    printf("============================================================\n");
    printf("[*] Target Scale : 100,000,000 Operations\n");
    printf("[*] Active Lanes : %d Hardware Cores\n\n", num_threads);

    pthread_t threads[MAX_THREADS];
    worker_arg_t args[MAX_THREADS];

    // High-precision clock start
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // Launch worker threads
    for (int i = 0; i < num_threads; i++) {
        args[i].thread_id = i;
        args[i].num_threads = num_threads;
        args[i].ops_completed = 0;
        pthread_create(&threads[i], NULL, worker_ring_simulation, &args[i]);
    }

    // Join worker threads
    unsigned long total_ops = 0;
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
        total_ops += args[i].ops_completed;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    // Calculate elapsed time in seconds
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    double ops_per_sec = total_ops / elapsed;

    printf("[-] Native C Execution Completed:\n");
    printf("    -> Total Operations : %lu\n", total_ops);
    printf("    -> Elapsed Time     : %.6f seconds\n", elapsed);
    printf("    -> Throughput (RPS) : %,.2f ops/sec\n", ops_per_sec);
    printf("============================================================\n");

    return 0;
}
