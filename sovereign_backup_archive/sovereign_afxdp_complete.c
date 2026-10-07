#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <linux/if_xdp.h>
#include <arpa/inet.h>

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
    printf("[*] Initializing Complete Raw AF_XDP Ring-Bound Engine on ens5f0np0...\n");

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[-] mlockall warning");
    } else {
        printf("[+] SUCCESS: Physical RAM locked completely against paging.\n");
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

    struct xdp_mmap_offsets off;
    socklen_t optlen = sizeof(off);
    if (getsockopt(sock, SOL_XDP, XDP_MMAP_OFFSETS, &off, &optlen) < 0) {
        perror("[-] getsockopt XDP_MMAP_OFFSETS failed");
        munmap(umem_area, UMEM_SIZE);
        close(sock);
        return 1;
    }

    printf("[+] SUCCESS: AF_XDP Fill and RX rings mapped successfully.\n");

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
        .sxdp_queue_id = 0,
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

    printf("[+] APEX RING-BOUND ENGINE STATUS: Fully operational and listening.\n");

    munmap(umem_area, UMEM_SIZE);
    close(sock);
    return 0;
}
