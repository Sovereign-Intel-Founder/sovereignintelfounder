#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>
#include <errno.h>
#include <sched.h>
#include <numaif.h>
#include <time.h>
#include <x86intrin.h>
#include "sovereign_bitstream.h"
#include "test_live_stream.h"
#include "sovereign_toll_bridge.h"
#include "sovereign_mesh_index.h"

void pin_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    int rc = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    if (rc != 0) {
        fprintf(stderr, "[-] WARNING: pthread_setaffinity_np failed for Core %d (code: %d)\n", core_id, rc);
    } else {
        printf("[*] Execution thread pinned to physical Core %d\n", core_id);
    }
}

static inline uint64_t get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

int main(void) {
    printf("[*] Initializing Sovereign Ultimate Low-Latency Engine...\n");
    pin_to_core(2);

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    } else {
        printf("[*] Physical RAM locked via mlockall.\n");
    }

    struct sched_param param;
    param.sched_priority = 99;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("[-] sched_setscheduler warning");
    } else {
        printf("[*] Real-time SCHED_FIFO priority (99) engaged.\n");
    }

    shm_unlink(SHM_NAME);
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR | O_EXCL, 0666);
    if (shm_fd == -1) { perror("shm_open failed"); exit(1); }
    if (ftruncate(shm_fd, SHM_SIZE) == -1) { perror("ftruncate failed"); exit(1); }
    if (fchmod(shm_fd, 0666) == -1) { perror("fchmod failed"); exit(1); }

    void *shm_ptr = mmap(NULL, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shm_ptr == MAP_FAILED) { perror("mmap failed"); exit(1); }

    unsigned long nodemask = 1; 
    if (mbind(shm_ptr, SHM_SIZE, MPOL_BIND, &nodemask, sizeof(nodemask) * 8 + 1, 0) != 0) {
        perror("[-] mbind NUMA warning");
    } else {
        printf("[*] Shared ring buffer explicitly bound to NUMA Node 0.\n");
    }

    madvise(shm_ptr, SHM_SIZE, MADV_WILLNEED);

    shared_ring_t *ring = (shared_ring_t *)shm_ptr;
    ring->head = 0;
    ring->tail = 0;

    mesh_router_t router;
    init_mesh_router(&router);

    uint64_t processed_count = 0;
    uint64_t passed_count = 0;
    uint64_t dropped_count = 0;

    printf("[*] Ultimate engine fully armed. Prefetch pipeline active...\n");

    while (1) {
        _mm_prefetch(&ring->frames[(ring->head + 2) % RING_CAPACITY], _MM_HINT_T0);

        uint64_t tail = __atomic_load_n(&ring->tail, __ATOMIC_ACQUIRE);
        uint64_t head = ring->head;

        if (head != tail) {
            uint64_t current_tsc = get_monotonic_ns();
            live_frame_t *frame = &ring->frames[head % RING_CAPACITY];
            
            if (validate_toll_bridge_frame(frame)) {
                passed_count++;
                route_mesh_frame_ultimate(&router, frame, current_tsc);
            } else {
                dropped_count++;
            }

            __atomic_store_n(&ring->head, head + 1, __ATOMIC_RELEASE);
            processed_count++;

            if (processed_count % 1000 == 0) {
                uint64_t avg_delta = router.total_routed > 0 ? (router.rolling_delta_sum / router.total_routed) : 0;
                printf("[+] Live-Proc: %lu | Pass: %lu | Jito Bundles: %lu | Relayer Dispatches: %lu | Avg Delta: %luns | Tips: %lu lamports\n",
                       processed_count, passed_count, router.jito_bundles_triggered, router.relayer_dispatches, avg_delta, router.total_tips_lamports);
            }
        } else {
            _mm_pause();
        }
    }

    munmap(shm_ptr, SHM_SIZE);
    close(shm_fd);
    return 0;
}
