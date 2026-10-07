#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <time.h>

#define PORT 9870

typedef struct {
    uint64_t term;
    uint64_t leader_id;
    uint64_t commit_index;
} __attribute__((aligned(64))) raft_heartbeat_t;

int main() {
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket creation failed");
        return 1;
    }

    int optval = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(int));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(PORT);

    if (bind(sockfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind failed");
        close(sockfd);
        return 1;
    }

    raft_heartbeat_t hb = { .term = 42, .leader_id = 1, .commit_index = 102400 };
    
    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    dest_addr.sin_port = htons(PORT);

    sendto(sockfd, &hb, sizeof(hb), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));

    raft_heartbeat_t rx_hb;
    socklen_t len = sizeof(dest_addr);
    recvfrom(sockfd, &rx_hb, sizeof(rx_hb), 0, (struct sockaddr *)&dest_addr, &len);

    printf("[+] Zero-Allocation Raft UDP Heartbeat Consensus packet exchanged.\n");
    printf("[+] Term: %lu | Leader ID: %lu | Commit Index: %lu\n", rx_hb.term, rx_hb.leader_id, rx_hb.commit_index);

    close(sockfd);
    return 0;
}
