#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <x86intrin.h>
#include "sovereign_bitstream.h"
#include "test_live_stream.h"

int main(void) {
    printf("[*] Initializing Sovereign Live Shared-Memory Ingestion Engine...\n");

    // Open or create shared memory segment for live stream
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open failed");
        exit(1);
    }

    if (ftruncate(shm_fd, SHM_SIZE) == -1) {
        perror("ftruncate failed");
        exit(1);
    }

    void *shm_ptr = mmap(NULL, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shm_ptr == MAP_FAILED) {
        perror("mmap failed");
        exit(1);
    }

    printf("[*] Live ring buffer active at %s (%d MB allocated).\n", SHM_NAME, SHM_SIZE / (1024 * 1024));
    printf("[*] Awaiting live data frames... (Press Ctrl+C to terminate)\n");

    volatile live_frame_t *ring = (volatile live_frame_t *)shm_ptr;
    uint64_t processed_count = 0;
    uint64_t start_cycle = __rdtsc();

    // Live continuous processing loop
    while (1) {
        // Polling live ring buffer slot for active sequence updates
        if (ring[processed_count % (SHM_SIZE / sizeof(live_frame_t))].sequence_id != 0) {
            // Process frame through core sovereign bitstream pipeline
            processed_count++;
            
            if (processed_count % 1000000 == 0) {
                uint64_t current_cycles = __rdtsc() - start_cycle;
                printf("[+] Processed %lu live frames. Current cycle delta: %lu\n", processed_count, current_cycles);
            }
        } else {
            // Yield CPU micro-slice to prevent burning a core during idle state
            _mm_pause();
        }
    }

    munmap(shm_ptr, SHM_SIZE);
    close(shm_fd);
    return 0;
}
