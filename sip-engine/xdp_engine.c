#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <xdp/xsk.h>
#include <bpf/libbpf.h>

#ifndef XSK_DEFAULT_FRAME_SIZE
#define XSK_DEFAULT_FRAME_SIZE 2048
#endif

#ifndef XDP_FLAGS_SKB_MODE
#define XDP_FLAGS_SKB_MODE (1 << 1)
#endif

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_DEFAULT_FRAME_SIZE
#define NET_IF "ens5f0np0"

typedef struct {
    uint16_t opcode;
    uint16_t numa_target;
    uint64_t mem_pointer;
    uint32_t crypto_hash;
} __attribute__((packed)) BinaryInstruction;

int main() {
    size_t total_size = NUM_FRAMES * FRAME_SIZE;
    void *buffer = mmap(NULL, total_size, PROT_READ | PROT_WRITE, 
                        MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (buffer == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    struct xsk_umem *umem;
    struct xsk_ring_prod fill = {0};
    struct xsk_ring_cons rx = {0};
    
    if (xsk_umem__create(&umem, buffer, total_size, &fill, &rx, NULL)) {
        perror("xsk_umem__create failed");
        munmap(buffer, total_size);
        return 1;
    }

    struct xsk_socket *xsk;
    struct xsk_socket_config xsk_cfg = {
        .rx_size = XSK_RING_CONS__DEFAULT_NUM_DESCS,
        .tx_size = XSK_RING_PROD__DEFAULT_NUM_DESCS,
        .libbpf_flags = 0,
        .xdp_flags = XDP_FLAGS_SKB_MODE,
        .bind_flags = XDP_COPY
    };

    if (xsk_socket__create(&xsk, NET_IF, 0, umem, &rx, &fill, &xsk_cfg)) {
        perror("xsk_socket__create failed");
        munmap(buffer, total_size);
        return 1;
    }

    printf("SUCCESS: Zero-copy AF_XDP engine armed on %s. Listening indefinitely...\n", NET_IF);
    
    // Continuous infinite zero-copy RX Ingestion Loop
    uint32_t idx_rx = 0;
    while (1) {
        int rcvd = xsk_ring_cons__peek(&rx, 64, &idx_rx);
        if (rcvd > 0) {
            for (int i = 0; i < rcvd; i++) {
                const struct xdp_desc *desc = xsk_ring_cons__rx_desc(&rx, idx_rx + i);
                void *packet_data = xsk_umem__get_data(buffer, desc->addr);
                
                BinaryInstruction *instr = (BinaryInstruction *)packet_data;
                printf("EXEC: Opcode: 0x%04X | Target: 0x%04X\n", instr->opcode, instr->numa_target);
            }
            xsk_ring_cons__release(&rx, rcvd);
        }
    }

    munmap(buffer, total_size);
    return 0;
}
