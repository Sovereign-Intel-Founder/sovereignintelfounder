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

#ifndef XDP_FILL_RING
#define XDP_FILL_RING 4
#endif
#ifndef XDP_RX_RING
#define XDP_RX_RING 2
#endif
#ifndef XDP_USE_NEED_WAKEUP
#define XDP_USE_NEED_WAKEUP (1 << 3)
#endif
#ifndef XDP_FLAGS_REPLACE
#define XDP_FLAGS_REPLACE (1 << 0)
#endif

#define NUM_FRAMES 2048
#define FRAME_SIZE 4096
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)

int main() {
    printf("[*] Initializing Sovereign AF_XDP Engine (Atomic Force-Replace Mode)...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        return 1;
    }

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

    DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);
    int ret = bpf_xdp_attach(ifindex, prog_fd, XDP_FLAGS_REPLACE, &opts);
    if (ret < 0) {
        bpf_xdp_detach(ifindex, 0, NULL);
        ret = bpf_xdp_attach(ifindex, prog_fd, 0, NULL);
        if (ret < 0) {
            ret = bpf_xdp_attach(ifindex, prog_fd, XDP_FLAGS_SKB_MODE, NULL);
            if (ret < 0) {
                fprintf(stderr, "[-] Critical: All bpf_xdp_attach methods failed: %s\n", strerror(-ret));
                return 1;
            }
            printf("[+] SUCCESS: Attached using XDP_FLAGS_SKB_MODE fallback.\n");
        } else {
            printf("[+] SUCCESS: Attached after clean detach.\n");
        }
    } else {
        printf("[+] SUCCESS: eBPF program atomically replaced/attached to ens5f0np0.\n");
    }

    int sock = socket(AF_XDP, SOCK_RAW, 0);
    if (sock < 0) {
        perror("[-] AF_XDP socket creation failed");
        return 1;
    }

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

    __u32 val = NUM_FRAMES;
    setsockopt(sock, SOL_XDP, XDP_RX_RING, &val, sizeof(val));
    setsockopt(sock, SOL_XDP, XDP_FILL_RING, &val, sizeof(val));

    int queue_id = 0;
    struct sockaddr_xdp sxdp = {
        .sxdp_family = AF_XDP,
        .sxdp_ifindex = ifindex,
        .sxdp_queue_id = queue_id,
        .sxdp_flags = XDP_COPY | XDP_USE_NEED_WAKEUP
    };

    if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
        perror("[-] bind AF_XDP failed");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }
    printf("[+] SUCCESS: AF_XDP socket bound cleanly!\n");

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
    printf("[+] SUCCESS: Socket FD inserted into xsks_map. Pipeline fully operational.\n");

    while (1) { sleep(1); }

    munmap(umem_area, UMEM_SIZE);
    close(sock);
    return 0;
}
