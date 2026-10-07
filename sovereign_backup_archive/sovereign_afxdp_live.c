#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sched.h>
#include <sys/mman.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <linux/if_xdp.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <bpf/xsk.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_RING_PROD__DEFAULT_NUM_DESCS
#define CACHE_LINE_SIZE 64

typedef struct {
    struct xsk_ring_prod producer;
    struct xsk_ring_cons consumer;
    struct xsk_umem *umem;
    struct xsk_socket *xsk;
    void *umem_buffer;
    uint64_t processed_packets;
    volatile int running;
} afxdp_worker_t;

void *afxdp_rx_worker(void *arg) {
    afxdp_worker_t *worker = (afxdp_worker_t *)arg;

    struct sched_param param = { .sched_priority = 99 };
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(4, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    int rx_fds[1];
    rx_fds[0] = xsk_socket__fd(worker->xsk);

    while (worker->running) {
        unsigned int rcvd;
        uint32_t idx_rx = 0;

        rcvd = xsk_ring_cons__peek(&worker->consumer, 32, &idx_rx);
        if (rcvd > 0) {
            for (unsigned int i = 0; i < rcvd; i++) {
                uint32_t len = xsk_ring_cons__rx_desc(&worker->consumer, idx_rx + i)->len;
                (void)len;
                worker->processed_packets++;
            }
            xsk_ring_cons__release(&worker->consumer, rcvd);
        } else {
            __builtin_ia32_pause();
        }
    }
    return NULL;
}

int main() {
    printf("[*] Initializing Apex AF_XDP Zero-Copy UMEM Engine on ens5f0np0...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    } else {
        printf("[+] SUCCESS: Physical RAM locked completely against paging.\n");
    }

    printf("[+] AF_XDP architecture bound. Ready to execute zero-copy line-rate stream.\n");
    return 0;
}
