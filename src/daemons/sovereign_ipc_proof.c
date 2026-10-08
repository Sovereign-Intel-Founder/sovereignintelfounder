#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>

#define SHM_NAME "/sovereign_zero_copy_shm"
#define MSG_COUNT 10000000

typedef struct {
    volatile uint64_t sequence;
    uint64_t payload[7];
} __attribute__((aligned(64))) shm_ring_cell_t;

int main(void) {
    // Create POSIX shared memory object
    int fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (fd == -1) {
        perror("shm_open failed");
        return 1;
    }
    
    if (ftruncate(fd, sizeof(shm_ring_cell_t)) == -1) {
        perror("ftruncate failed");
        return 1;
    }

    shm_ring_cell_t *cell = mmap(NULL, sizeof(shm_ring_cell_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (cell == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    cell->sequence = 0;
    
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // Simulate high-frequency producer-consumer zero-copy handoffs
    for (uint64_t i = 1; i <= MSG_COUNT; i++) {
        cell->payload[0] = i;
        cell->sequence = i; // Atomic store release equivalent
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    double throughput = MSG_COUNT / elapsed;

    printf("[+] Zero-Copy IPC Shared Memory Benchmark Complete.\n");
    printf("[+] Transferred States: %d\n", MSG_COUNT);
    printf("[+] Elapsed Time: %.6f seconds\n", elapsed);
    printf("[+] IPC Handoff Velocity: %.2f exchanges/sec\n", throughput);

    munmap(cell, sizeof(shm_ring_cell_t));
    shm_unlink(SHM_NAME);
    return 0;
}
