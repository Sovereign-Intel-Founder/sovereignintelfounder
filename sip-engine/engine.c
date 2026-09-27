#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>

#define SHM_NAME "/sip_ring_buffer"
#define RING_SIZE 1048576 // 1MB ring buffer
#define ITERATIONS 1000000

typedef struct {
    uint16_t opcode;
    uint16_t numa_target;
    uint64_t mem_pointer;
    uint32_t crypto_hash;
} __attribute__((packed)) BinaryInstruction;

int main() {
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open failed");
        return 1;
    }
    ftruncate(shm_fd, RING_SIZE);
    
    BinaryInstruction *ring = mmap(0, RING_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (ring == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }
    
    printf("SUCCESS: 1MB shared ring buffer mapped at memory address %p\n", (void*)ring);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // High-speed ingestion of 1 million 16-byte instruction frames
    for (uint64_t i = 0; i < ITERATIONS; i++) {
        ring[i % (RING_SIZE / sizeof(BinaryInstruction))] = (BinaryInstruction){
            .opcode = 0x01FA,
            .numa_target = 0x0002,
            .mem_pointer = 0x7FFF00004000 + i,
            .crypto_hash = 0x8F3C9A12 + (uint32_t)i
        };
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    long nanoseconds = (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec);
    
    printf("BENCHMARK: Processed %d 16-byte frames in %ld ns (%.2f ns per instruction)\n", 
           ITERATIONS, nanoseconds, (double)nanoseconds / ITERATIONS);

    shm_unlink(SHM_NAME);
    return 0;
}
