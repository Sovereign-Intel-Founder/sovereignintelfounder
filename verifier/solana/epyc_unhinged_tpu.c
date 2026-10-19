#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sched.h>

#define THREADS 64
#define BURST_ITERATIONS 100000

typedef struct {
    int thread_id;
    unsigned char* cached_packet;
    size_t packet_len;
    long sent_count;
} ThreadContext;

void* unhinged_worker(void* arg) {
    ThreadContext* ctx = (ThreadContext*)arg;

    // Pin each thread brutally to its own dedicated EPYC hardware core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(ctx->thread_id % 128, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) pthread_exit(NULL);

    // Optimize socket send buffer for massive unthrottled bursts
    int sndbuf = 1048576; // 1MB buffer per socket
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf));

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(8004);
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);

    long local_sent = 0;
    for (int i = 0; i < BURST_ITERATIONS; i++) {
        ssize_t ret = sendto(sock, ctx->cached_packet, ctx->packet_len, 0,
                             (const struct sockaddr *)&servaddr, sizeof(servaddr));
        if (ret > 0) {
            local_sent++;
        }
    }

    close(sock);
    ctx->sent_count = local_sent;
    pthread_exit(NULL);
}

int main() {
    printf("[!] INITIALIZING UNHINGED EPYC TPU FIREHOSE...\n");

    // Construct a raw, aggressive transaction wire template
    size_t pkt_len = 256;
    unsigned char* template_packet = malloc(pkt_len);
    memset(template_packet, 0, pkt_len);
    template_packet[0] = 0x01; // Mock signature count header
    memset(template_packet + 1, 0xef, 64); // Aggressive payload signature pattern

    pthread_t threads[THREADS];
    ThreadContext contexts[THREADS];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < THREADS; i++) {
        contexts[i].thread_id = i;
        contexts[i].cached_packet = template_packet;
        contexts[i].packet_len = pkt_len;
        contexts[i].sent_count = 0;
        pthread_create(&threads[i], NULL, unhinged_worker, &contexts[i]);
    }

    long grand_total = 0;
    for (int i = 0; i < THREADS; i++) {
        pthread_join(threads[i], NULL);
        grand_total += contexts[i].sent_count;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("\n[+] ==========================================\n");
    printf("[+] UNHINGED PIPELINE EXECUTION COMPLETE\n");
    printf("[+] Total Packets Dispatched: %ld\n", grand_total);
    printf("[+] Duration: %.4f seconds\n", elapsed);
    printf("[+] Raw Firehose Velocity: %.2f Mpkts/sec\n", (grand_total / elapsed) / 1e6);
    printf("[+] ==========================================\n");

    free(template_packet);
    return 0;
}
