/*
 * Sovereign Intelligence Protocol (SIP) - Bounded SPSC Ring Buffer Subsystem
 * Lock-free Single-Producer Single-Consumer (SPSC) ring buffer with 
 * acquire/release memory ordering semantics.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <assert.h>
#include <pthread.h>
#include <unistd.h>

#define RING_SIZE 1024  // Usable capacity is RING_SIZE - 1 due to full/empty separation

typedef struct {
    uint64_t buffer[RING_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} spsc_ring_t;

void spsc_ring_init(spsc_ring_t *ring) {
    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);
}

bool spsc_ring_push(spsc_ring_t *ring, uint64_t val) {
    size_t head = atomic_load_explicit(&ring->head, memory_order_relaxed);
    size_t tail = atomic_load_explicit(&ring->tail, memory_order_acquire);
    
    if ((head + 1) % RING_SIZE == tail) {
        return false; // Full / Backpressure shed
    }
    
    ring->buffer[head] = val;
    atomic_store_explicit(&ring->head, (head + 1) % RING_SIZE, memory_order_release);
    return true;
}

bool spsc_ring_pop(spsc_ring_t *ring, uint64_t *val) {
    size_t tail = atomic_load_explicit(&ring->tail, memory_order_relaxed);
    size_t head = atomic_load_explicit(&ring->head, memory_order_acquire);
    
    if (tail == head) {
        return false; // Empty
    }
    
    *val = ring->buffer[tail];
    atomic_store_explicit(&ring->tail, (tail + 1) % RING_SIZE, memory_order_release);
    return true;
}

#define STRESS_ITEMS 50000
typedef struct {
    spsc_ring_t *ring;
    uint64_t produced_sum;
    uint64_t consumed_sum;
    bool success;
} thread_arg_t;

static void *producer_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t *)arg;
    uint64_t sum = 0;
    for (uint64_t i = 1; i <= STRESS_ITEMS; i++) {
        while (!spsc_ring_push(targ->ring, i)) {
            sched_yield();
        }
        sum += i;
    }
    targ->produced_sum = sum;
    return NULL;
}

static void *consumer_thread(void *arg) {
    thread_arg_t *targ = (thread_arg_t *)arg;
    uint64_t sum = 0;
    uint64_t count = 0;
    uint64_t val = 0;
    
    while (count < STRESS_ITEMS) {
        if (spsc_ring_pop(targ->ring, &val)) {
            sum += val;
            count++;
        } else {
            sched_yield();
        }
    }
    targ->consumed_sum = sum;
    targ->success = (targ->produced_sum == 0 || targ->produced_sum == targ->consumed_sum);
    return NULL;
}

int main(void) {
    printf("[C-Subsystem] Initializing SPSC Ring Buffer rigorous test suite...\n");
    
    spsc_ring_t ring;
    spsc_ring_init(&ring);

    uint64_t val = 0;
    assert(spsc_ring_pop(&ring, &val) == false);
    assert(spsc_ring_push(&ring, 42) == true);
    assert(spsc_ring_pop(&ring, &val) == true);
    assert(val == 42);
    assert(spsc_ring_pop(&ring, &val) == false);
    printf("[C-Subsystem] Basic assertions: PASS\n");

    spsc_ring_init(&ring);
    for (size_t i = 0; i < RING_SIZE - 1; i++) {
        assert(spsc_ring_push(&ring, i) == true);
    }
    assert(spsc_ring_push(&ring, 999) == false);
    printf("[C-Subsystem] Full-capacity boundary & backpressure: PASS\n");

    spsc_ring_init(&ring);
    for (int cycle = 0; cycle < 5; cycle++) {
        for (uint64_t i = 0; i < 500; i++) {
            assert(spsc_ring_push(&ring, i + (cycle * 1000)) == true);
        }
        for (uint64_t i = 0; i < 500; i++) {
            uint64_t popped = 0;
            assert(spsc_ring_pop(&ring, &popped) == true);
            assert(popped == i + (cycle * 1000));
        }
    }
    printf("[C-Subsystem] Ring wraparound & FIFO order: PASS\n");

    spsc_ring_init(&ring);
    pthread_t p_thread, c_thread;
    thread_arg_t targ = { .ring = &ring, .produced_sum = 0, .consumed_sum = 0, .success = false };
    
    uint64_t expected_sum = 0;
    for (uint64_t i = 1; i <= STRESS_ITEMS; i++) expected_sum += i;
    targ.produced_sum = expected_sum;

    pthread_create(&c_thread, NULL, consumer_thread, &targ);
    pthread_create(&p_thread, NULL, producer_thread, &targ);

    pthread_join(p_thread, NULL);
    pthread_join(c_thread, NULL);

    assert(targ.consumed_sum == expected_sum);
    printf("[C-Subsystem] Concurrent Pthread SPSC stress test (%d items): PASS\n", STRESS_ITEMS);

    printf("[C-Subsystem] All C verification tests PASSED cleanly.\n");
    return 0;
}
