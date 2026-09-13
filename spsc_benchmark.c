#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <time.h>

#define RING_SIZE 4096
#define ITERATIONS 1000000

typedef struct {
    atomic_size_t head;
    atomic_size_t tail;
    long buffer[RING_SIZE];
} spsc_ring_t;

spsc_ring_t ring;

void* producer(void* arg) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(2, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
    
    for (size_t i = 0; i < ITERATIONS; i++) {
        size_t tail = atomic_load_explicit(&ring.tail, memory_order_relaxed);
        while (((tail + 1) % RING_SIZE) == atomic_load_explicit(&ring.head, memory_order_acquire)) {
            // spin-wait queue full
        }
        ring.buffer[tail] = (long)i;
        atomic_store_explicit(&ring.tail, (tail + 1) % RING_SIZE, memory_order_release);
    }
    return NULL;
}

void* consumer(void* arg) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(3, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
    
    size_t received = 0;
    while (received < ITERATIONS) {
        size_t head = atomic_load_explicit(&ring.head, memory_order_relaxed);
        if (head == atomic_load_explicit(&ring.tail, memory_order_acquire)) {
            continue; // queue empty
        }
        long val = ring.buffer[head];
        atomic_store_explicit(&ring.head, (head + 1) % RING_SIZE, memory_order_release);
        received++;
    }
    return NULL;
}

int main() {
    atomic_init(&ring.head, 0);
    atomic_init(&ring.tail, 0);
    
    pthread_t prod, cons;
    struct timespec start, end;
    
    clock_gettime(CLOCK_MONOTONIC, &start);
    pthread_create(&prod, NULL, producer, NULL);
    pthread_create(&cons, NULL, consumer, NULL);
    
    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    long elapsed = (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec);
    printf("SPSC Ring Benchmark: %d items passed in %ld ns (~%Ld ns/msg)\n", 
           ITERATIONS, elapsed, (long double)elapsed / ITERATIONS);
    return 0;
}
