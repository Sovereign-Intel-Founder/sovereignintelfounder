#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/net_tstamp.h>
#include <linux/sockios.h>

int main() {
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed (requires root or CAP_NET_RAW)");
        return 1;
    }

    struct hwtstamp_config hwcfg;
    memset(&hwcfg, 0, sizeof(hwcfg));
    hwcfg.tx_type = HWTSTAMP_TX_ON;
    hwcfg.rx_filter = HWTSTAMP_FILTER_ALL;

    printf("[+] PTP hardware timestamp configuration structure defined.\n");
    printf("[+] Target flags: SOF_TIMESTAMPING_RAW_HARDWARE / HWTSTAMP_TX_ON\n");

    close(sockfd);
    return 0;
}
