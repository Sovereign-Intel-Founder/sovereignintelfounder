#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdatomic.h>

#define SHM_RING_NAME "/hft_ipc_ring_buffer"
#define RING_CAPACITY 4096

typedef struct {
    uint64_t timestamp;
    uint32_t symbol_id;
    uint32_t bid_price;
    uint32_t ask_price;
} __attribute__((aligned(64))) ipc_tick_t;

typedef struct {
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
    ipc_tick_t buffer[RING_CAPACITY];
} __attribute__((aligned(64))) shm_ring_t;

int main() {
    int fd = shm_open(SHM_RING_NAME, O_CREAT | O_RDWR, 0666);
    if (fd < 0) {
        perror("shm_open failed");
        return 1;
    }
    ftruncate(fd, sizeof(shm_ring_t));

    shm_ring_t *ring = mmap(NULL, sizeof(shm_ring_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ring == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);

    printf("[+] POSIX Shared Memory Inter-Process Ring Buffer initialized.\n");
    printf("[+] Ring Size: %lu bytes | Capacity: %d ticks\n", sizeof(shm_ring_t), RING_CAPACITY);

    munmap(ring, sizeof(shm_ring_t));
    close(fd);
    shm_unlink(SHM_RING_NAME);
    return 0;
}
