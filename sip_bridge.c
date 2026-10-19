#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include "sip_sentinel.h"

#define SHM_NAME "/sip_shm_channel"
#define SHM_SIZE 4096

// External reference to your flattened state-machine logic from core_logic.c
extern uint64_t compute_secure_token(uint64_t seed);

int main(int argc, char *argv[]) {
    sip_sentinel_init();

    // Create or open POSIX shared memory object
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0660);
    if (shm_fd < 0) {
        perror("[!] Failed to open POSIX shared memory");
        exit(1);
    }

    if (ftruncate(shm_fd, SHM_SIZE) < 0) {
        perror("[!] Failed to set shared memory size");
        exit(1);
    }

    // Map shared memory into process address space
    void *ptr = mmap(0, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (ptr == MAP_FAILED) {
        perror("[!] Failed to map shared memory");
        exit(1);
    }

    printf("[*] SIP Shared Memory Bridge active at %s. Waiting for ingestion input...\n", SHM_NAME);

    volatile uint64_t *input_seed = (volatile uint64_t *)ptr;
    volatile uint64_t *output_token = (volatile uint64_t *)((char *)ptr + 8);
    volatile uint32_t *status_flag = (volatile uint32_t *)((char *)ptr + 16);

    *status_flag = 0;

    // High-performance polling / execution loop
    while (1) {
        if (*status_flag == 1) { // New data signal from ingestion pipeline
            uint64_t seed = *input_seed;
            *output_token = compute_secure_token(seed);
            *status_flag = 2; // Signal processing complete
        }
        usleep(100); // Low-latency yield
    }

    return 0;
}
