#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <poll.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <xdp/xsk.h>
#include <bpf/libbpf.h>

#ifndef XSK_DEFAULT_FRAME_SIZE
#define XSK_DEFAULT_FRAME_SIZE 2048
#endif

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_DEFAULT_FRAME_SIZE
#define NET_IF "veth-int"

#define SHM_NAME "/sip_ring_buffer"
#define RING_SIZE 1048576

typedef struct {
    uint16_t opcode;
    uint16_t numa_target;
    uint64_t mem_pointer;
    uint32_t crypto_hash;
} __attribute__((packed)) BinaryInstruction;

int main() {
    struct rlimit rlim = { .rlim_cur = RLIM_INFINITY, .rlim_max = RLIM_INFINITY };
    setrlimit(RLIMIT_MEMLOCK, &rlim);

    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) { perror("shm_open failed"); return 1; }
    ftruncate(shm_fd, RING_SIZE);
    BinaryInstruction *ring = mmap(0, RING_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (ring == MAP_FAILED) { perror("mmap failed"); return 1; }

    void *umem_buffer = NULL;
    size_t umem_size = NUM_FRAMES * FRAME_SIZE;
    if (posix_memalign(&umem_buffer, getpagesize(), umem_size)) {
        perror("posix_memalign failed");
        return 1;
    }

    struct xsk_umem *umem = NULL;
    struct xsk_ring_prod fill_q;
    struct xsk_ring_cons comp_q;
    if (xsk_umem__create(&umem, umem_buffer, umem_size, &fill_q, &comp_q, NULL)) {
        perror("xsk_umem__create failed");
        return 1;
    }

    struct xsk_socket *xsk = NULL;
    struct xsk_ring_cons rx_q;
    struct xsk_ring_prod tx_q;
    struct xsk_socket_config xsk_cfg = {
        .rx_size = XSK_RING_CONS__DEFAULT_NUM_DESCS,
        .tx_size = XSK_RING_PROD__DEFAULT_NUM_DESCS,
        .xdp_flags = XDP_FLAGS_SKB_MODE,
    };

    if (xsk_socket__create(&xsk, NET_IF, 0, umem, &rx_q, &tx_q, &xsk_cfg)) {
        perror("xsk_socket__create failed");
        return 1;
    }

    printf("ENGINE LIVE: Polling packets on %s...\n", NET_IF);
    
    struct pollfd fds = { .fd = xsk_socket__fd(xsk), .events = POLLIN };
    uint64_t ring_index = 0;

    while (1) {
        int ret = poll(&fds, 1, 1000);
        if (ret <= 0) continue;

        uint32_t idx_rx = 0;
        uint32_t rcvd = xsk_ring_cons__peek(&rx_q, 64, &idx_rx);
        if (!rcvd) continue;

        for (uint32_t i = 0; i < rcvd; i++) {
            uint64_t addr = xsk_ring_cons__rx_desc(&rx_q, idx_rx + i)->addr;
            void *pkt_data = xsk_umem__get_data(umem_buffer, addr);
            
            // Skip 42 bytes of network headers (Ethernet + IPv4 + UDP)
            void *payload_ptr = (void *)((uint8_t *)pkt_data + 42);
            ring[ring_index % (RING_SIZE / sizeof(BinaryInstruction))] = *(BinaryInstruction *)payload_ptr;
            ring_index++;
        }
        xsk_ring_cons__release(&rx_q, rcvd);
    }
    return 0;
}
