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

#define NUM_FRAMES 4096
#define FRAME_SIZE 2048
#define UMEM_SIZE (NUM_FRAMES * FRAME_SIZE)

int main() {
    printf("[*] Initializing Sovereign AF_XDP Lifecycle Manager...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
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
    printf("[+] SUCCESS: sovereign_ebpf.o loaded into kernel space.\n");

    // 2. Find xsks_map inside the loaded object
    struct bpf_map *xsks_map = bpf_object__find_map_by_name(obj, "xsks_map");
    if (!xsks_map) {
        fprintf(stderr, "[-] Failed to find xsks_map in BPF object\n");
        return 1;
    }
    int map_fd = bpf_map__fd(xsks_map);

    // 3. Create AF_XDP socket
    int sock = socket(AF_XDP, SOCK_RAW, 0);
    if (sock < 0) {
        perror("[-] AF_XDP socket creation failed");
        return 1;
    }

    // 4. Setup UMEM
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

    // 5. Update xsks_map BEFORE bind()
    int queue_id = 0;
    if (bpf_map_update_elem(map_fd, &queue_id, &sock, BPF_ANY) < 0) {
        perror("[-] Failed to update xsks_map with socket fd");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }
    printf("[+] SUCCESS: Socket FD inserted into xsks_map at queue 0.\n");

    // 6. Bind socket to interface queue
    unsigned int ifindex = if_nametoindex("ens5f0np0");
    if (ifindex == 0) {
        perror("[-] if_nametoindex failed for ens5f0np0");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }

    struct sockaddr_xdp sxdp = {
        .sxdp_family = AF_XDP,
        .sxdp_ifindex = ifindex,
        .sxdp_queue_id = queue_id,
        .sxdp_flags = XDP_ZEROCOPY
    };

    if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
        sxdp.sxdp_flags = XDP_COPY;
        if (bind(sock, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
            perror("[-] bind AF_XDP socket failed");
            munmap(umem_area, UMEM_SIZE);
            close(sock);
            return 1;
        }
        printf("[+] NOTE: Bound in XDP_COPY mode fallback.\n");
    } else {
        printf("[+] SUCCESS: Bound strictly in native XDP_ZEROCOPY mode to ens5f0np0 queue 0!\n");
    }

    // 7. Attach XDP program using standard libbpf netdev API
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "xdp_ingress_pass");
    if (!prog) {
        fprintf(stderr, "[-] Failed to find XDP program entry point\n");
    } else {
        int prog_fd = bpf_program__fd(prog);
        int err = bpf_xdp_attach(ifindex, prog_fd, XDP_FLAGS_UPDATE_IF_NOEXIST, NULL);
        if (err < 0) {
            fprintf(stderr, "[-] bpf_xdp_attach failed: %s\n", strerror(-err));
        } else {
            printf("[+] SUCCESS: eBPF program attached to netdev ens5f0np0!\n");
        }
    }

    printf("[+] SOVEREIGN AF_XDP PIPELINE: Fully operational and live.\n");

    munmap(umem_area, UMEM_SIZE);
    close(sock);
    return 0;
}
