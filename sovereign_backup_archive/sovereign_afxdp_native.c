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

#ifndef SOL_XDP
#define SOL_XDP 283
#endif
#ifndef XDP_UMEM_REG
#define XDP_UMEM_REG 1
#endif
#ifndef XDP_RX_RING
#define XDP_RX_RING 2
#endif
#ifndef XDP_TX_RING
#define XDP_TX_RING 3
#endif
#ifndef XDP_FILL_RING
#define XDP_FILL_RING 4
#endif
#ifndef XDP_COMPLETION_RING
#define XDP_COMPLETION_RING 5
#endif

#define NUM_FRAMES 2048
#define FRAME_SIZE 4096
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)

int main() {
    printf("[*] Initializing Sovereign AF_XDP Engine (Native mlx5 Driver Mode)...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        return 1;
    }

    // 1. Load BPF Object and Program
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

    // 2. Attach in NATIVE mode (flag = 0 lets driver choose optimal hardware offload/driver path)
    if (bpf_xdp_attach(ifindex, prog_fd, 0, NULL) < 0) {
        perror("[-] bpf_xdp_attach native mode failed");
        return 1;
    }
    printf("[+] SUCCESS: eBPF program attached in NATIVE driver mode on mlx5!\n");

    // 3. Create Raw AF_XDP Socket
    int sock = socket(AF_XDP, SOCK_RAW, 0);
    if (sock < 0) {
        perror("[-] AF_XDP socket creation failed");
        return 1;
    }

    // 4. Setup UMEM via mmap
    void *umem_area = mmap(NULL, UMEM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (umem_area == MAP_FAILED) {
        perror("[-] UMEM mmap failed");
        close(sock);
        return 1;
    }

    struct xdp_umem_reg mr = {
        .addr = (__u64)umem_area,
        .len = UMEM_SIZE,
        .chunk_size = FRAME_SIZE,
        .headroom = 0
    };

    if (setsockopt(sock, SOL_XDP, XDP_UMEM_REG, &mr, sizeof(mr)) < 0) {
        perror("[-] setsockopt XDP_UMEM_REG failed");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }

    // 5. Configure all 4 rings
    __u32 val = NUM_FRAMES;
    setsockopt(sock, SOL_XDP, XDP_RX_RING, &val, sizeof(val));
    setsockopt(sock, SOL_XDP, XDP_TX_RING, &val, sizeof(val));
    setsockopt(sock, SOL_XDP, XDP_FILL_RING, &val, sizeof(val));
    setsockopt(sock, SOL_XDP, XDP_COMPLETION_RING, &val, sizeof(val));

    // 6. Bind Socket (Native mode uses zero copy if supported, fallback to copy if needed)
    int queue_id = 0;
    struct sockaddr_xdp sxdp = {
        .sxdp_family = AF_XDP,
        .sxdp_ifindex = ifindex,
        .sxdp_queue_id = queue_id,
        .sxdp_flags = 0 // Try zero-copy native first
    };

    if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
        printf("[*] Zero-copy bind unavailable, falling back to XDP_COPY...\n");
        sxdp.sxdp_flags = XDP_COPY;
        if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
            perror("[-] bind AF_XDP native failed");
            munmap(umem_area, UMEM_SIZE);
            close(sock);
            return 1;
        }
    }
    printf("[+] SUCCESS: Raw AF_XDP socket bound natively to queue 0!\n");

    // 7. Populate XSKMAP
    struct bpf_map *xsks_map = bpf_object__find_map_by_name(obj, "xsks_map");
    if (!xsks_map) {
        bpf_object__for_each_map(xsks_map, obj) {
            if (bpf_map__type(xsks_map) == BPF_MAP_TYPE_XSKMAP) break;
        }
    }
    if (!xsks_map) {
        fprintf(stderr, "[-] Failed to locate xsks_map\n");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }

    int map_fd = bpf_map__fd(xsks_map);
    if (bpf_map_update_elem(map_fd, &queue_id, &sock, BPF_ANY) < 0) {
        perror("[-] Failed to update xsks_map");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }
    printf("[+] SUCCESS: Socket FD inserted into xsks_map. Sovereign Pipeline fully operational.\n");

    while (1) { sleep(1); }

    munmap(umem_area, UMEM_SIZE);
    close(sock);
    return 0;
}
