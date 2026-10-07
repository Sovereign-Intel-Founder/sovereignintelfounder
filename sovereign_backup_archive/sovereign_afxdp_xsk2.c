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
    printf("[*] Initializing Sovereign AF_XDP Engine (libxdp API)...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        return 1;
    }

    // 1. Load BPF Object
    struct bpf_object *obj = bpf_object__open_file("sovereign_ebpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "[-] Failed to open sovereign_ebpf.o\n");
        return 1;
    }
    if (bpf_object__load(obj) < 0) {
        fprintf(stderr, "[-] Failed to load BPF object\n");
        return 1;
    }

    struct bpf_program *prog = NULL;
    struct bpf_program *iter_prog;
    bpf_object__for_each_program(iter_prog, obj) {
        prog = iter_prog;
        break;
    }
    if (!prog) {
        fprintf(stderr, "[-] No BPF programs found\n");
        return 1;
    }

    int prog_fd = bpf_program__fd(prog);
    bpf_xdp_detach(ifindex, 0, NULL);
    if (bpf_xdp_attach(ifindex, prog_fd, 0, NULL) < 0) {
        if (bpf_xdp_attach(ifindex, prog_fd, XDP_FLAGS_SKB_MODE, NULL) < 0) {
            perror("[-] bpf_xdp_attach failed");
            return 1;
        }
        printf("[+] SUCCESS: Attached using SKB mode.\n");
    } else {
        printf("[+] SUCCESS: Attached in native mode.\n");
    }

    // 2. Setup UMEM and XSK Socket using libxdp helpers
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
        .xdp_flags = 0,
        .bind_flags = XDP_COPY
    };

    int queue_id = 0;
    ret = xsk_socket__create(&xsk, "ens5f0np0", queue_id, umem, &rx, &tx, &xsk_cfg);
    if (ret) {
        xsk_cfg.bind_flags = 0;
        ret = xsk_socket__create(&xsk, "ens5f0np0", queue_id, umem, &rx, &tx, &xsk_cfg);
        if (ret) {
            fprintf(stderr, "[-] xsk_socket__create failed: %s\n", strerror(-ret));
            return 1;
        }
    }
    printf("[+] SUCCESS: Official xsk socket created and bound!\n");

    // 3. Populate XSKMAP
    struct bpf_map *xsks_map = bpf_object__find_map_by_name(obj, "xsks_map");
    if (!xsks_map) {
        fprintf(stderr, "[-] Failed to locate xsks_map\n");
        return 1;
    }

    int map_fd = bpf_map__fd(xsks_map);
    int xsk_fd = xsk_socket__fd(xsk);
    if (bpf_map_update_elem(map_fd, &queue_id, &xsk_fd, BPF_ANY) < 0) {
        perror("[-] Failed to update xsks_map");
        return 1;
    }
    printf("[+] SUCCESS: Socket FD inserted into xsks_map. Pipeline fully operational.\n");

    while (1) { sleep(1); }

    return 0;
}
