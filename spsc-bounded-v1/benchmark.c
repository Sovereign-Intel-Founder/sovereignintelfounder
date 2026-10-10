#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>
#include <time.h>
#define RING_BUFFER_SIZE 65536
#define TOTAL_EVENTS 1000000
typedef struct { uint64_t seq; char data[64]; } Event;
typedef struct { Event buffer[RING_BUFFER_SIZE]; atomic_size_t head; atomic_size_t tail; } SPSCRing;
SPSCRing ring;
atomic_bool finished = false;
uint64_t consumed_count = 0;
void* consumer_thread(void* arg) {
    size_t tail = 0;
    while (!atomic_load(&finished) || tail != atomic_load_explicit(&ring.head, memory_order_acquire)) {
        size_t head = atomic_load_explicit(&ring.head, memory_order_acquire);
        while (tail != head) { consumed_count++; tail = (tail + 1) & (RING_BUFFER_SIZE - 1);
            atomic_store_explicit(&ring.tail, tail, memory_order_release); }
    }
    return NULL;
}
int main() {
    atomic_init(&ring.head, 0); atomic_init(&ring.tail, 0);
    pthread_t t; pthread_create(&t, NULL, consumer_thread, NULL);
    struct timespec start, end; clock_gettime(CLOCK_MONOTONIC, &start);
    for (uint64_t i = 0; i < TOTAL_EVENTS; i++) {
        size_t h = atomic_load_explicit(&ring.head, memory_order_relaxed);
        size_t tail = atomic_load_explicit(&ring.tail, memory_order_acquire);
        while (((h + 1) & (RING_BUFFER_SIZE - 1)) == tail) { tail = atomic_load_explicit(&ring.tail, memory_order_acquire); }
        ring.buffer[h].seq = i;
        atomic_store_explicit(&ring.head, (h + 1) & (RING_BUFFER_SIZE - 1), memory_order_release);
    }
    atomic_store(&finished, true); pthread_join(t, NULL);
    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("[+] SPSC Verified: %lu events in %.4fs (%.2f EPS)\n", consumed_count, elapsed, TOTAL_EVENTS / elapsed);
    return 0;
}
