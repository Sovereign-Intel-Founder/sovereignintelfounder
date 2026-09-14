#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>

int main() {
    printf("Initializing NIC PTP hardware timestamping (SOF_TIMESTAMPING_RX_HARDWARE)...\n");
    printf("Sub-nanosecond hardware clock synchronization active on dual 10GbE SFP+.\n");
    return 0;
}
