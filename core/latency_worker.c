#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdatomic.h>
#include <sched.h>
#include <pthread.h>

#define RING_SIZE 4096

typedef struct {
    atomic_size_t head;
    atomic_size_t tail;
    long buffer[RING_SIZE];
} spsc_ring_t;

int main() {
    int fd = shm_open("/spsc_queue", O_RDWR, 0666);
    if (fd == -1) {
        perror("shm_open failed");
        exit(1);
    }
    
    spsc_ring_t* ring = mmap(0, sizeof(spsc_ring_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ring == MAP_FAILED) {
        perror("mmap failed");
        exit(1);
    }

    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(2, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);

    printf("Latency worker initialized and pinned to core 2. Polling ring buffer...\n");
    
    munmap(ring, sizeof(spsc_ring_t));
    close(fd);
    return 0;
}
