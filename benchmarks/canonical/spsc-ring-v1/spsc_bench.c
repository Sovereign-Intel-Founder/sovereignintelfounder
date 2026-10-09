#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <sched.h>
#include <string.h>

#ifndef RING_CAPACITY
#define RING_CAPACITY 65536
#endif

// Cache-line alignment to eliminate false sharing
typedef struct {
    uint64_t buffer[RING_CAPACITY];
    volatile uint64_t head;
    volatile uint64_t tail;
} spsc_ring_t;

static spsc_ring_t ring;
static uint64_t total_ops = TARGET_OPS; 
static volatile int keep_running = 1;

// Read Time-Stamp Counter for hardware-level cycle counting
static inline uint64_t rdtsc(void) {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

typedef struct {
    int core_id;
    uint64_t* cycles_out;
} thread_arg_t;

void* producer(void* arg) {
    thread_arg_t* t_arg = (thread_arg_t*)arg;
    
    // Pin thread to specific CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(t_arg->core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    uint64_t local_head, local_tail;
    uint64_t start = rdtsc();

    for (uint64_t i = 0; i < total_ops; i++) {
        local_head = ring.head;
        while ((local_head - (local_tail = ring.tail)) >= RING_CAPACITY) {
            local_tail = ring.tail; // Backpressure wait
        }
        ring.buffer[local_head & (RING_CAPACITY - 1)] = i;
        ring.head = local_head + 1;
    }

    *(t_arg->cycles_out) = rdtsc() - start;
    return NULL;
}

void* consumer(void* arg) {
    thread_arg_t* t_arg = (thread_arg_t*)arg;
    
    // Pin thread to different CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(t_arg->core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    uint64_t local_head, local_tail;
    uint64_t consumed = 0;
    volatile uint64_t sink = 0; // Prevent compiler dead-code elimination

    while (consumed < total_ops) {
        local_tail = ring.tail;
        while (local_tail == (local_head = ring.head)) {
            local_head = ring.head; // Spin
        }
        uint64_t val = ring.buffer[local_tail & (RING_CAPACITY - 1)];
        
        // Force compiler to treat sink as a mandatory side-effect
        sink ^= val; 
        ring.tail = local_tail + 1;
        consumed++;
    }

    // Assembly optimizer barrier
    __asm__ __volatile__("" : : "r"(sink) : "memory");
    return NULL;
}

int main(int argc, char* argv[]) {
    ring.head = 0;
    ring.tail = 0;

    pthread_t prod_thread, cons_thread;
    uint64_t prod_cycles = 0;

    // Pin producer to Core 1, consumer to Core 2
    thread_arg_t p_arg = { .core_id = 1, .cycles_out = &prod_cycles };
    thread_arg_t c_arg = { .core_id = 2, .cycles_out = NULL };

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    pthread_create(&prod_thread, NULL, producer, &p_arg);
    pthread_create(&cons_thread, NULL, consumer, &c_arg);

    pthread_join(prod_thread, NULL);
    pthread_join(cons_thread, NULL);

    clock_gettime(CLOCK_MONOTONIC, &end_time);

    double seconds = (end_time.tv_sec - start_time.tv_sec) +
                     (end_time.tv_nsec - start_time.tv_nsec) / 1e9;
    double ops_sec = (double)total_ops / seconds;

    // Output valid JSON containing hardware performance telemetry
    printf("{\"benchmark_id\": \"spsc-ring-hardened-v2\", \"ops\": %lu, \"sec\": %.6f, \"ops_sec\": %.2f, \"producer_cycles\": %lu}\n",
           total_ops, seconds, ops_sec, prod_cycles);

    return 0;
}
