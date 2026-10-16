#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <x86intrin.h>
#include <sched.h>

#define ITERATIONS 1000000

typedef struct {
    uint64_t timestamp;
    uint32_t sequence;
    uint32_t price;
} __attribute__((aligned(64))) market_tick_t;

static volatile market_tick_t ring_buffer;
static volatile int completed = 0;

void *producer_thread(void *arg) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    for (uint32_t i = 0; i < ITERATIONS; i++) {
        uint64_t tsc = __rdtsc();
        ring_buffer.timestamp = tsc;
        ring_buffer.sequence = i;
        ring_buffer.price = 10000 + (i % 50);
        __atomic_thread_fence(__ATOMIC_RELEASE);
    }
    return NULL;
}

void *consumer_thread(void *arg) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(4, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    uint64_t total_cycles = 0;
    uint32_t last_seq = 0;
    
    while (last_seq < ITERATIONS - 1) {
        __atomic_thread_fence(__ATOMIC_ACQUIRE);
        uint32_t current_seq = ring_buffer.sequence;
        if (current_seq != last_seq) {
            uint64_t latency = __rdtsc() - ring_buffer.timestamp;
            total_cycles += latency;
            last_seq = current_seq;
        }
    }
    printf("[+] HFT Tick-to-Trade Average Latency: %lu CPU cycles over %d ticks\n", total_cycles / ITERATIONS, ITERATIONS);
    return NULL;
}

int main() {
    pthread_t p, c;
    pthread_create(&p, NULL, producer_thread, NULL);
    pthread_create(&c, NULL, consumer_thread, NULL);
    pthread_join(p, NULL);
    pthread_join(c, NULL);
    return 0;
}
