#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define RING_SIZE 1024

typedef struct {
    atomic_size_t head;
    atomic_size_t tail;
    long buffer[RING_SIZE];
} spsc_ring_t;

int main() {
    int fd = shm_open("/spsc_queue", O_CREAT | O_RDWR, 0666);
    ftruncate(fd, sizeof(spsc_ring_t));
    spsc_ring_t* ring = mmap(0, sizeof(spsc_ring_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);
    printf("Lock-free SPSC ring initialized in shared memory at %p\n", (void*)ring);
    munmap(ring, sizeof(spsc_ring_t));
    shm_unlink("/spsc_queue");
    return 0;
}
