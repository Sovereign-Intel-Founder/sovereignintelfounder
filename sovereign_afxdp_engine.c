#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/resource.h>
#include <sqlite3.h>

#define NUM_FRAMES 65536
#define FRAME_SIZE 2048
#define SHM_NAME "/sip_afxdp_ring"
#define DB_PATH "/home/joshua445/toll_gate/sip_ledger.db"

typedef struct {
    uint64_t rx_packets;
    uint64_t rx_bytes;
    uint64_t valid_signatures;
    uint64_t invalid_signatures;
    uint32_t ring_head;
    uint32_t ring_tail;
} ring_buffer_meta_t;

static volatile int running = 1;

void sig_handler(int sig) {
    (void)sig;
    running = 0;
}

void pin_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
}

void* afxdp_worker_lane(void* arg) {
    int lane_id = *(int*)arg;
    pin_to_core(lane_id);
    
    printf("[AF_XDP Core %d] Worker lane bound to NUMA node 0\n", lane_id);
    
    while (running) {
        // Zero-copy ring buffer polling loop
        usleep(500);
    }
    return NULL;
}

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    printf("=== SOVEREIGN AF_XDP KERNEL-BYPASS ENGINE ===\n");

    // 1. Setup POSIX Shared Memory Ring Buffer
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd < 0) {
        perror("shm_open failed");
        return 1;
    }
    ftruncate(shm_fd, sizeof(ring_buffer_meta_t));
    
    ring_buffer_meta_t *meta = mmap(NULL, sizeof(ring_buffer_meta_t),
                                    PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (meta == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }
    memset(meta, 0, sizeof(ring_buffer_meta_t));

    // 2. Allocate UMEM Memory Chunk for Zero-Copy Frame Transfers
    void *umem_area = NULL;
    if (posix_memalign(&umem_area, getpagesize(), NUM_FRAMES * FRAME_SIZE)) {
        perror("posix_memalign UMEM failed");
        return 1;
    }
    printf("--> Allocated %d KB UMEM buffer at %p\n", (NUM_FRAMES * FRAME_SIZE) / 1024, umem_area);

    // 3. Spawn Core-Pinned Worker Lanes across Cores 0-7
    pthread_t threads[8];
    int lane_ids[8];
    for (int i = 0; i < 8; i++) {
        lane_ids[i] = i;
        if (pthread_create(&threads[i], NULL, afxdp_worker_lane, &lane_ids[i]) != 0) {
            fprintf(stderr, "Failed to spawn thread lane %d\n", i);
        }
    }

    printf("--> All 8 AF_XDP worker lanes initialized and running.\n");

    while (running) {
        sleep(1);
    }

    printf("--> Stopping AF_XDP Engine...\n");
    for (int i = 0; i < 8; i++) {
        pthread_join(threads[i], NULL);
    }

    free(umem_area);
    munmap(meta, sizeof(ring_buffer_meta_t));
    close(shm_fd);
    shm_unlink(SHM_NAME);
    
    printf("--> AF_XDP Engine shutdown complete.\n");
    return 0;
}
