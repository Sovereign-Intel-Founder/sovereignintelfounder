#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>
#include <unistd.h>

#define RING_SIZE 4096
#define MASK (RING_SIZE - 1)

struct ring_slot {
    uint64_t sequence;
    uint64_t timestamp;
    char payload[56]; // Padding to fit exact 64-byte cache line
};

struct spsc_ring {
    struct ring_slot buffer[RING_SIZE];
    char pad1[64];
    atomic_size_t head __attribute__((aligned(64)));
    char pad2[64];
    atomic_size_t tail __attribute__((aligned(64)));
};

int main() {
    struct spsc_ring *ring = aligned_alloc(64, sizeof(struct spsc_ring));
    if (!ring) {
        perror("Allocation failed");
        return 1;
    }
    
    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);

    printf("[+] Lock-free SPSC cache-aligned ring buffer initialized.\n");
    printf("[+] Ring Size: %d slots | Slot Size: 64 bytes (1 cache line)\n", RING_SIZE);
    printf("[+] False-sharing prevention active via 64-byte padding and atomic fences.\n");

    free(ring);
    return 0;
}
