#!/bin/bash
echo "[+] Halting previous daemon instances..."
pkill -9 sip_daemon 2>/dev/null || true
pkill -f "head -c 128" 2>/dev/null || true

echo "[+] Writing ultimate multi-feed high-performance sip_daemon.c..."
cat << 'C_CODE' > sip_daemon.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <fcntl.h>
#include <errno.h>
#include <stdatomic.h>

#define PORT 9872
#define MAX_EVENTS 64
#define RING_BUFFER_SIZE 65536

typedef struct {
    char data[256];
    size_t len;
} Packet;

typedef struct {
    Packet buffer[RING_BUFFER_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} LockFreeRing;

static LockFreeRing ring = { .head = 0, .tail = 0 };
static atomic_ulong total_ingested = 0;
static atomic_ulong total_routed = 0;

void* worker_thread(void* arg) {
    (void)arg;
    Packet pkt;
    while (1) {
        size_t current_tail = atomic_load(&ring.tail);
        size_t current_head = atomic_load(&ring.head);
        
        if (current_tail != current_head) {
            pkt = ring.buffer[current_tail % RING_BUFFER_SIZE];
            atomic_store(&ring.tail, current_tail + 1);
            atomic_fetch_add(&total_routed, 1);
        } else {
            usleep(100);
        }
    }
    return NULL;
}

int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int main() {
    int server_fd, epoll_fd;
    struct sockaddr_in address;
    struct epoll_event ev, events[MAX_EVENTS];
    int opt = 1;

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    set_nonblocking(server_fd);

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, SOMAXCONN) < 0) {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }

    epoll_fd = epoll_create1(0);
    if (epoll_fd == -1) {
        perror("epoll_create1 failed");
        exit(EXIT_FAILURE);
    }

    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = server_fd;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, &ev) == -1) {
        perror("epoll_ctl server_fd failed");
        exit(EXIT_FAILURE);
    }

    pthread_t worker;
    pthread_create(&worker, NULL, worker_thread, NULL);

    printf("[DAEMON] Sovereign Intelligence Protocol ULTIMATE NODE OPERATIONAL on port %d (epoll + lock-free ring)\n", PORT);
    fflush(stdout);

    while (1) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 1000);
        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == server_fd) {
                struct sockaddr_in client_addr;
                socklen_t client_len = sizeof(client_addr);
                int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
                if (client_fd >= 0) {
                    set_nonblocking(client_fd);
                    ev.events = EPOLLIN | EPOLLET | EPOLLONESHOT;
                    ev.data.fd = client_fd;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev);
                }
            } else {
                int client_fd = events[i].data.fd;
                char buf[256];
                ssize_t count = read(client_fd, buf, sizeof(buf));
                if (count > 0) {
                    size_t current_head = atomic_load(&ring.head);
                    size_t current_tail = atomic_load(&ring.tail);
                    if ((current_head - current_tail) < RING_BUFFER_SIZE) {
                        memcpy(ring.buffer[current_head % RING_BUFFER_SIZE].data, buf, count);
                        ring.buffer[current_head % RING_BUFFER_SIZE].len = count;
                        atomic_store(&ring.head, current_head + 1);
                        atomic_fetch_add(&total_ingested, 1);
                    }
                    printf("[DAEMON TELEMETRY] Multi-Feed Ingested: %ld bytes | Total Ingested: %lu | Total Routed: %lu\n", 
                           count, atomic_load(&total_ingested), atomic_load(&total_routed));
                    fflush(stdout);
                }
                close(client_fd);
            }
        }
    }
    return 0;
}
C_CODE

echo "[+] Compiling ultimate high-performance binary..."
gcc -std=c11 -O3 -march=native -fomit-frame-pointer -flto -Wall sip_daemon.c -o sip_daemon -lpthread
if [ $? -ne 0 ]; then
    echo "[-] Compilation failed."
    exit 1
fi

echo "[+] Launching ultimate daemon..."
./sip_daemon > sip_daemon.log 2>&1 &
DAEMON_PID=$!
echo "[+] Daemon PID: $DAEMON_PID"

sleep 1

echo "[+] Starting multi-source traffic generator loop..."
while true; do
    # Simulating mixed feeds: JSON RPC / Websocket / System Telemetry
    echo '{"source":"solana_rpc","event":"mempool_tx","data":"0x7f8a..."}' | nc -w 1 127.0.0.1 9872 >/dev/null 2>&1
    head -c 128 /dev/urandom > /dev/tcp/127.0.0.1/9872 2>/dev/null || true
    sleep 0.05
done &
STREAM_PID=$!

echo "[+] Ultimate Node Active! Check logs with: tail -f sip_daemon.log"
