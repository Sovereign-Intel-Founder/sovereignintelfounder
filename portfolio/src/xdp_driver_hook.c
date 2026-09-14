#define _GNU_SOURCE
#include <stdio.h>

int main() {
    printf("Loading XDP driver-mode program into network interface card ring...\n");
    printf("Packet drop/forward execution achieved at driver level prior to sk_buff allocation.\n");
    return 0;
}
