#include <x86intrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include "sovereign_bitstream.h"

#define ITERATIONS 500000000

static BitstreamRingBuffer global_ring;
static volatile int keep_running = 1;

void *producer_worker(void *arg) {
    (void)arg;
    uint8_t payload[64] = "SOVEREIGN_POLYMORPHIC_STREAM_PAYLOAD_V1";
    uint64_t sent = 0;
    while (sent < ITERATIONS) {
        if (bitstream_enqueue(&global_ring, payload, 64, 0xDEADBEEF)) {
            sent++;
        }
    }
    return NULL;
}

void *consumer_worker(void *arg) {
    (void)arg;
    BitstreamFrame frame;
    uint64_t received = 0;
    uint64_t start_cycle = __rdtsc();

    while (received < ITERATIONS) {
        if (bitstream_dequeue(&global_ring, &frame)) {
            received++;
        }
    }
    uint64_t end_cycle = __rdtsc();
    printf("[+] Successfully processed %lu polymorphic frames in %lu CPU cycles.\n", received, (end_cycle - start_cycle));
    return NULL;
}

int main(void) {
    printf("[*] Initializing Sovereign Polymorphic Bitstream Engine...\n");
    bitstream_ring_init(&global_ring);

    pthread_t prod, cons;
    pthread_create(&cons, NULL, consumer_worker, NULL);
    pthread_create(&prod, NULL, producer_worker, NULL);

    pthread_join(prod, NULL);
    pthread_join(cons, NULL);

    printf("[+] Bitstream benchmark execution completed cleanly.\n");
    return 0;
}
