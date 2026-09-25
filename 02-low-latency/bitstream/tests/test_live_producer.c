#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>
#include "sovereign_bitstream.h"
#include "test_live_stream.h"

int main(void) {
    printf("[*] Initializing Temporal-Stamping Ingestion Producer...\n");

    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) { perror("shm_open failed"); exit(1); }
    if (ftruncate(shm_fd, SHM_SIZE) == -1) { perror("ftruncate failed"); exit(1); }

    void *shm_ptr = mmap(NULL, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shm_ptr == MAP_FAILED) { perror("mmap failed"); exit(1); }

    shared_ring_t *ring = (shared_ring_t *)shm_ptr;
    uint64_t seq = 0;

    printf("[*] Producer active. Stamping hardware TSC fragments into stream...\n");

    while (1) {
        uint64_t tail = ring->tail;
        uint64_t head = ring->head;

        if (((tail + 1) % RING_CAPACITY) != (head % RING_CAPACITY)) {
            live_frame_t *frame = &ring->frames[tail % RING_CAPACITY];
            
            frame->sequence_id = seq++;
            frame->capture_tsc = __rdtsc(); // Capture exact microsecond fragment timestamp
            frame->payload_length = 239;
            frame->flags = 0xA5;
            memset(frame->data, 0x5A, sizeof(frame->data));

            __atomic_store_n(&ring->tail, tail + 1, __ATOMIC_RELEASE);
        } else {
            _mm_pause();
        }
    }

    munmap(shm_ptr, SHM_SIZE);
    close(shm_fd);
    return 0;
}
