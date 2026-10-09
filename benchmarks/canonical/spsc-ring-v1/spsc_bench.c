#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <stdatomic.h>
#include <time.h>

#define RING_CAP 65536
#define MASK (RING_CAP - 1)
#define OPS 10000000

typedef struct {
    uint64_t data[RING_CAP];
    _Atomic size_t head;
    _Atomic size_t tail;
} spsc_ring_t;

spsc_ring_t ring;
void *producer(void *arg) {
    for (uint64_t i = 1; i <= OPS; i++) {
        while (i - atomic_load_explicit(&ring.tail, memory_order_relaxed) > RING_CAP) { __builtin_ia32_pause(); }
        atomic_store_explicit(&ring.data[i & MASK], i, memory_order_relaxed);
        atomic_store_explicit(&ring.head, i, memory_order_release);
    }
    return NULL;
}
void *consumer(void *arg) {
    uint64_t received = 0;
    while (received < OPS) {
        while (atomic_load_explicit(&ring.head, memory_order_acquire) == received) { __builtin_ia32_pause(); }
        received++;
        uint64_t val = atomic_load_explicit(&ring.data[received & MASK], memory_order_relaxed);
        if (val != received) { fprintf(stderr, "Mismatch\n"); exit(1); }
    }
    return NULL;
}
int main() {
    pthread_t p, c;
    atomic_init(&ring.head, 0); atomic_init(&ring.tail, 0);
    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    pthread_create(&p, NULL, producer, NULL); pthread_create(&c, NULL, consumer, NULL);
    pthread_join(p, NULL); pthread_join(c, NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double sec = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    printf("{\"benchmark_id\": \"spsc-ring-v1\", \"ops\": %lu, \"sec\": %.4f, \"ops_sec\": %.2f}\n", OPS, sec, OPS/sec);
    return 0;
}
