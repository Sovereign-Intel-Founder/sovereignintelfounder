#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
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

#ifndef XSK_LIBXDP_FLAGS_INHIBIT_PROG_LOAD
#define XSK_LIBXDP_FLAGS_INHIBIT_PROG_LOAD 1
#endif

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_UMEM__DEFAULT_FRAME_SIZE
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)
#define BATCH_SIZE 64

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <interface_name>\n", argv[0]);
        fprintf(stderr, "Example: %s ens5f0np1\n", argv[0]);
        return 1;
    }

    const char *ifname = argv[1];
    printf("[*] Launching Sovereign AF_XDP Active Ingestion Engine on %s...\n", ifname);

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        fprintf(stderr, "[-] Interface %s not found\n", ifname);
        return 1;
    }

    // 1. Load eBPF Object
    struct bpf_object *obj = bpf_object__open_file("sovereign_ebpf.o", NULL);
    if (libbpf_get_error(obj) || bpf_object__load(obj) < 0) {
        fprintf(stderr, "[-] Failed to load BPF object\n");
        return 1;
    }

    struct bpf_program *prog = NULL, *iter_prog;
    bpf_object__for_each_program(iter_prog, obj) { prog = iter_prog; break; }
    if (!prog) return 1;

    // 2. Attach program natively
    int prog_fd = bpf_program__fd(prog);
    bpf_xdp_detach(ifindex, 0, NULL);
    if (bpf_xdp_attach(ifindex, prog_fd, 0, NULL) < 0) {
        perror("[-] bpf_xdp_attach failed");
        return 1;
    }
    printf("[+] Native eBPF program attached to %s.\n", ifname);

    // 3. Allocate UMEM buffer
    void *umem_buffer = NULL;
    if (posix_memalign(&umem_buffer, getpagesize(), UMEM_SIZE)) {
        fprintf(stderr, "[-] posix_memalign failed\n");
        return 1;
    }

    struct xsk_umem *umem = NULL;
    struct xsk_ring_prod fill = {0};
    struct xsk_ring_cons comp = {0};

    struct xsk_umem_config umem_cfg = {
        .fill_size = NUM_FRAMES,
        .comp_size = NUM_FRAMES,
        .frame_size = FRAME_SIZE,
        .frame_headroom = 0,
        .flags = 0
    };

    if (xsk_umem__create(&umem, umem_buffer, UMEM_SIZE, &fill, &comp, &umem_cfg)) {
        fprintf(stderr, "[-] xsk_umem__create failed\n");
        return 1;
    }

    // 4. Create AF_XDP socket without overriding eBPF program
    struct xsk_socket *xsk = NULL;
    struct xsk_ring_cons rx = {0};
    struct xsk_ring_prod tx = {0};

    struct xsk_socket_config xsk_cfg = {
        .rx_size = NUM_FRAMES,
        .tx_size = NUM_FRAMES,
        .libxdp_flags = XSK_LIBXDP_FLAGS_INHIBIT_PROG_LOAD,
        .xdp_flags = 0,
        .bind_flags = 0
    };

    int queue_id = 0;
    if (xsk_socket__create(&xsk, ifname, queue_id, umem, &rx, &tx, &xsk_cfg)) {
        fprintf(stderr, "[-] xsk_socket__create failed\n");
        return 1;
    }

    // 5. Populate BPF XSKMAP
    struct bpf_map *xsks_map = bpf_object__find_map_by_name(obj, "xsks_map");
    if (!xsks_map) {
        bpf_object__for_each_map(xsks_map, obj) {
            if (bpf_map__type(xsks_map) == BPF_MAP_TYPE_XSKMAP) break;
        }
    }
    int map_fd = bpf_map__fd(xsks_map);
    int xsk_fd = xsk_socket__fd(xsk);
    bpf_map_update_elem(map_fd, &queue_id, &xsk_fd, BPF_ANY);

    // 6. Populate FILL ring so driver has initial frames to write packets into
    uint32_t idx_fill = 0;
    if (xsk_ring_prod__reserve(&fill, NUM_FRAMES / 2, &idx_fill) == NUM_FRAMES / 2) {
        for (int i = 0; i < NUM_FRAMES / 2; i++) {
            *xsk_ring_prod__fill_addr(&fill, idx_fill++) = i * FRAME_SIZE;
        }
        xsk_ring_prod__submit(&fill, NUM_FRAMES / 2);
    }

    printf("[+] AF_XDP Engine operational. Draining RX ring...\n");

    // 7. Active Poll Packet Ingestion Loop
    struct pollfd pfd = {
        .fd = xsk_fd,
        .events = POLLIN
    };

    uint64_t total_packets = 0;

    while (1) {
        uint32_t idx_rx = 0;
        uint32_t rcvd = xsk_ring_cons__peek(&rx, BATCH_SIZE, &idx_rx);

        if (!rcvd) {
            poll(&pfd, 1, 1000);
            continue;
        }

        // Process batch
        for (uint32_t i = 0; i < rcvd; i++) {
            const struct xdp_desc *desc = xsk_ring_cons__rx_desc(&rx, idx_rx++);
            total_packets++;
        }

        xsk_ring_cons__release(&rx, rcvd);

        // Replenish FILL ring with consumed buffers
        if (xsk_ring_prod__reserve(&fill, rcvd, &idx_fill) == rcvd) {
            for (uint32_t i = 0; i < rcvd; i++) {
                *xsk_ring_prod__fill_addr(&fill, idx_fill++) = idx_rx * FRAME_SIZE;
            }
            xsk_ring_prod__submit(&fill, rcvd);
        }

        if (total_packets > 0 && total_packets % 100000 == 0) {
            printf("[+] Processed %lu packets\n", total_packets);
        }
    }

    return 0;
}
