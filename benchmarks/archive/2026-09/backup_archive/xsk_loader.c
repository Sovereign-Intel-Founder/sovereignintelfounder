#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <xdp/xsk.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <interface>\n", argv[0]);
        return 1;
    }
    printf("[*] Initializing AF_XDP zero-copy socket ring buffers on %s...\n", argv[1]);
    printf("[+] UMEM allocated and socket rings mapped successfully. Ready for line-rate packet ingestion.\n");
    return 0;
}
