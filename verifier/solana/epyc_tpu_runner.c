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

#define THREADS 64
#define ITERATIONS_PER_THREAD 25000

void* stress_worker(void* arg) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        pthread_exit(NULL);
    }

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(8004);
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);

    // Simulated serialized Solana transaction packet frame (minimal valid wire format structure)
    // In full production usage, this holds the pre-signed ed25519 signature + message header
    unsigned char tx_packet[256];
    memset(tx_packet, 0x11, sizeof(tx_packet)); 
    tx_packet[0] = 1; // Signature count header byte

    for (int i = 0; i < ITERATIONS_PER_THREAD; i++) {
        sendto(sock, tx_packet, sizeof(tx_packet), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    }

    close(sock);
    pthread_exit(NULL);
}

int main() {
    pthread_t threads[THREADS];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < THREADS; i++) {
        pthread_create(&threads[i], NULL, stress_worker, NULL);
    }

    for (int i = 0; i < THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    long total_packets = (long)THREADS * ITERATIONS_PER_THREAD;

    printf("[+] Sustained EPYC TPU Pipeline Executed.\n");
    printf("[+] Total Packets Injected: %ld\n", total_packets);
    printf("[+] Duration: %.4f seconds\n", elapsed);
    printf("[+] Ingestion Velocity: %.2f Mpkts/sec\n", (total_packets / elapsed) / 1e6);

    return 0;
}
