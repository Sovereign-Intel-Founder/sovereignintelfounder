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
#include <bpf/xsk.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_UMEM__DEFAULT_FRAME_SIZE
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)

int main() {
    printf("[*] Initializing Sovereign AF_XDP Engine (Native libbpf XSK API)...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        return 1;
    }

    // 1. Open and load BPF object
    struct bpf_object *obj = bpf_object__open_file("sovereign_ebpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "[-] Failed to open sovereign_ebpf.o\n");
        return 1;
    }
    if (bpf_object__load(obj) < 0) {
        fprintf(stderr, "[-] Failed to load BPF object into kernel\n");
        return 1;
    }

    struct bpf_program *prog = NULL;
    struct bpf_program *iter_prog;
    bpf_object__for_each_program(iter_prog, obj) {
        prog = iter_prog;
        break;
    }
    if (!prog) {
        fprintf(stderr, "[-] Critical: No BPF programs found\n");
        return 1;
    }

    int prog_fd = bpf_program__fd(prog);
    
    // Clear and attach XDP program
    bpf_xdp_detach(ifindex, 0, NULL);
    if (bpf_xdp_attach(ifindex, prog_fd, 0, NULL) < 0) {
        perror("[-] Critical: bpf_xdp_attach failed");
        return 1;
    }
    printf("[+] SUCCESS: eBPF program attached to ens5f0np0.\n");

    // 2. Allocate UMEM via libbpf helper
    void *umem_buffer = NULL;
    if (posix_memalign(&umem_buffer, getpagesize(), UMEM_SIZE)) {
        fprintf(stderr, "[-] UMEM buffer alignment failed\n");
        return 1;
    }

    struct xsk_umem *umem = NULL;
    struct xsk_ring_prod fill_ring;
    struct xsk_ring_cons comp_ring;

    struct xsk_umem_config umem_cfg = {
        .fill_size = NUM_FRAMES,
        .comp_size = NUM_FRAMES,
        .frame_size = FRAME_SIZE,
        .frame_headroom = 0,
        .flags = 0
    };

    int ret = xsk_umem__create(&umem, umem_buffer, UMEM_SIZE, &fill_ring, &comp_ring, &umem_cfg);
    if (ret) {
        fprintf(stderr, "[-] xsk_umem__create failed: %s\n", strerror(-ret));
        free(umem_buffer);
        return 1;
    }
    printf("[+] SUCCESS: UMEM allocated and registered via libbpf.\n");

    // 3. Create and bind XDP socket using libbpf xsk API
    struct xsk_socket *xsk = NULL;
    struct xsk_ring_cons rx_ring;
    struct xsk_ring_prod tx_ring;
    
    struct xsk_socket_config xsk_cfg = {
        .rx_size = XSK_RING_CONS__DEFAULT_NUM_DESCS,
        .tx_size = XSK_RING_PROD__DEFAULT_NUM_DESCS,
        .libbpf_flags = 0,
        .xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST,
        .bind_flags = XDP_COPY
    };

    int queue_id = 0;
    ret = xsk_socket__create(&xsk, "ens5f0np0", queue_id, umem, &rx_ring, &tx_ring, &xsk_cfg);
    if (ret) {
        fprintf(stderr, "[-] xsk_socket__create failed: %s. Trying fallback flags...\n", strerror(-ret));
        xsk_cfg.bind_flags = XDP_COPY;
        ret = xsk_socket__create(&xsk, "ens5f0np0", queue_id, umem, &rx_ring, &tx_ring, &xsk_cfg);
        if (ret) {
            fprintf(stderr, "[-] Critical: xsk_socket__create completely failed: %s\n", strerror(-ret));
            return 1;
        }
    }
    printf("[+] SUCCESS: AF_XDP socket created and bound via libbpf!\n");

    // 4. Update the BPF map (`xsks_map`) with the active socket FD
    struct bpf_map *xsks_map = bpf_object__find_map_by_name(obj, "xsks_map");
    if (!xsks_map) {
        bpf_object__for_each_map(xsks_map, obj) {
            if (bpf_map__type(xsks_map) == BPF_MAP_TYPE_XSKMAP) break;
        }
    }

    if (!xsks_map) {
        fprintf(stderr, "[-] Critical: Failed to locate xsks_map\n");
        return 1;
    }

    int map_fd = bpf_map__fd(xsks_map);
    int xsk_fd = xsk_socket__fd(xsk);
    if (bpf_map_update_elem(map_fd, &queue_id, &xsk_fd, BPF_ANY) < 0) {
        perror("[-] Failed to update xsks_map");
        return 1;
    }
    printf("[+] SUCCESS: Socket FD inserted into xsks_map at queue 0. Pipeline fully operational.\n");

    while (1) {
        sleep(1);
    }

    return 0;
}
