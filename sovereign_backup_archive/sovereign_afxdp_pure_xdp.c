#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <linux/if_xdp.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <xdp/xsk.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_UMEM__DEFAULT_FRAME_SIZE
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)

int main() {
    printf("[*] Initializing Sovereign AF_XDP Engine (Pure libxdp Unified Mode)...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        return 1;
    }

    // Setup UMEM and XSK Socket via libxdp (letting libxdp handle program binding cleanly)
    struct xsk_umem *umem = NULL;
    struct xsk_socket *xsk = NULL;
    void *umem_buffer = NULL;

    int ret = posix_memalign(&umem_buffer, getpagesize(), UMEM_SIZE);
    if (ret) {
        fprintf(stderr, "[-] UMEM buffer alignment failed\n");
        return 1;
    }

    struct xsk_umem_config umem_cfg = {
        .fill_size = NUM_FRAMES,
        .comp_size = NUM_FRAMES,
        .frame_size = FRAME_SIZE,
        .frame_headroom = 0,
        .flags = 0
    };

    struct xsk_ring_prod fill = {0};
    struct xsk_ring_cons comp = {0};

    ret = xsk_umem__create(&umem, umem_buffer, UMEM_SIZE, &fill, &comp, &umem_cfg);
    if (ret) {
        fprintf(stderr, "[-] xsk_umem__create failed: %s\n", strerror(-ret));
        free(umem_buffer);
        return 1;
    }

    struct xsk_ring_cons rx = {0};
    struct xsk_ring_prod tx = {0};

    struct xsk_socket_config xsk_cfg = {
        .rx_size = XSK_RING_CONS__DEFAULT_NUM_DESCS,
        .tx_size = XSK_RING_PROD__DEFAULT_NUM_DESCS,
        .libxdp_flags = 0,
        .xdp_flags = XDP_FLAGS_SKB_MODE, // Fallback to SKB mode safely for the high-core host
        .bind_flags = 0                  // Zero flags to bypass driver constraint rejections
    };

    int queue_id = 0;
    ret = xsk_socket__create(&xsk, "ens5f0np0", queue_id, umem, &rx, &tx, &xsk_cfg);
    if (ret) {
        fprintf(stderr, "[-] xsk_socket__create failed: %s\n", strerror(-ret));
        return 1;
    }
    printf("[+] SUCCESS: libxdp socket created, UMEM registered, and interface bound!\n");

    while (1) { sleep(1); }

    return 0;
}
