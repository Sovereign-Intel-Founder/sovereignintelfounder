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

#define NUM_FRAMES 2048
#define FRAME_SIZE 4096
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)

int main() {
    printf("[*] Initializing Sovereign AF_XDP Engine (Dynamic Program Resolution)...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    }

    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        return 1;
    }

    // 1. Open and load BPF object via libbpf
    struct bpf_object *obj = bpf_object__open_file("sovereign_ebpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "[-] Failed to open sovereign_ebpf.o\n");
        return 1;
    }
    if (bpf_object__load(obj) < 0) {
        fprintf(stderr, "[-] Failed to load BPF object into kernel\n");
        return 1;
    }

    // 2. Dynamically find the first program in the object file
    struct bpf_program *prog = NULL;
    struct bpf_program *iter_prog;
    bpf_object__for_each_program(iter_prog, obj) {
        prog = iter_prog;
        printf("[+] Discovered BPF program section: '%s' (name: '%s')\n", 
               bpf_program__section_name(prog), bpf_program__name(prog));
        break; // Take the primary entry point
    }

    if (!prog) {
        fprintf(stderr, "[-] Critical: No BPF programs found in sovereign_ebpf.o\n");
        return 1;
    }

    int prog_fd = bpf_program__fd(prog);
    
    // 3. Attach XDP program to netdev FIRST (Required before socket bind)
    bpf_xdp_detach(ifindex, XDP_FLAGS_UPDATE_IF_NOEXIST, NULL);
    if (bpf_xdp_attach(ifindex, prog_fd, 0, NULL) < 0) {
        perror("[-] Critical: bpf_xdp_attach failed");
        return 1;
    }
    printf("[+] SUCCESS: eBPF program attached to netdev ens5f0np0.\n");

    // 4. Find xsks_map dynamically or by name
    struct bpf_map *xsks_map = bpf_object__find_map_by_name(obj, "xsks_map");
    if (!xsks_map) {
        // Fallback: search by map type or iterate maps if name differs
        struct bpf_map *iter_map;
        bpf_object__for_each_map(iter_map, obj) {
            if (bpf_map__type(iter_map) == BPF_MAP_TYPE_XSKMAP) {
                xsks_map = iter_map;
                printf("[+] Discovered XSKMAP by type: '%s'\n", bpf_map__name(iter_map));
                break;
            }
        }
    }

    if (!xsks_map) {
        fprintf(stderr, "[-] Critical: Failed to locate xsks_map in BPF object\n");
        return 1;
    }
    int map_fd = bpf_map__fd(xsks_map);

    // 5. Create AF_XDP socket
    int sock = socket(AF_XDP, SOCK_RAW, 0);
    if (sock < 0) {
        perror("[-] AF_XDP socket creation failed");
        return 1;
    }

    // 6. Setup UMEM
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

    // 7. Update xsks_map BEFORE bind()
    int queue_id = 0;
    if (bpf_map_update_elem(map_fd, &queue_id, &sock, BPF_ANY) < 0) {
        perror("[-] Failed to update xsks_map with socket fd");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }
    printf("[+] SUCCESS: Socket FD inserted into xsks_map at queue 0.\n");

    // 8. Bind socket to interface queue
    struct sockaddr_xdp sxdp = {
        .sxdp_family = AF_XDP,
        .sxdp_ifindex = ifindex,
        .sxdp_queue_id = queue_id,
        .sxdp_flags = XDP_ZEROCOPY
    };

    if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
        sxdp.sxdp_flags = XDP_COPY;
        if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
            perror("[-] Critical: bind AF_XDP failed even with XDP_COPY");
            munmap(umem_area, UMEM_SIZE);
            close(sock);
            return 1;
        }
        printf("[+] NOTE: Bound successfully using XDP_COPY fallback mode.\n");
    } else {
        printf("[+] SUCCESS: Bound strictly in native XDP_ZEROCOPY mode!\n");
    }

    printf("[+] SOVEREIGN AF_XDP ENGINE: Pipeline fully initialized and operational.\n");

    munmap(umem_area, UMEM_SIZE);
    close(sock);
    return 0;
}
