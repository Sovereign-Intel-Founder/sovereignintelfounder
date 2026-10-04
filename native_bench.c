#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define THREADS 50
#define REQUESTS_PER_THREAD 200
#define TOTAL_REQUESTS (THREADS * REQUESTS_PER_THREAD)
#define PORT 8080

static double latencies[TOTAL_REQUESTS];
static _Atomic int total_completed = 0;

void* worker(void* arg) {
    int sockfd = -1;
    struct sockaddr_in serv_addr = {0};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);

    int opt = 1;

    for (int i = 0; i < REQUESTS_PER_THREAD; i++) {
        while (sockfd < 0) {
            sockfd = socket(AF_INET, SOCK_STREAM, 0);
            setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));
            if (connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
                close(sockfd);
                sockfd = -1;
                usleep(100);
            }
        }

        const char *req = "GET / HTTP/1.1\r\nHost: localhost\r\nX-Client-ID: bench_worker\r\n\r\n";
        int req_len = strlen(req);
        char buf[512];

        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC_RAW, &t0);

        ssize_t w = write(sockfd, req, req_len);
        if (w <= 0) {
            close(sockfd);
            sockfd = -1;
            i--;
            continue;
        }

        ssize_t r = read(sockfd, buf, sizeof(buf));
        if (r <= 0) {
            close(sockfd);
            sockfd = -1;
            i--;
            continue;
        }

        clock_gettime(CLOCK_MONOTONIC_RAW, &t1);
        double lat = (t1.tv_sec - t0.tv_sec) * 1000.0 + (t1.tv_nsec - t0.tv_nsec) / 1000000.0;

        int idx = __atomic_fetch_add(&total_completed, 1, __ATOMIC_RELAXED);
        if (idx < TOTAL_REQUESTS) {
            latencies[idx] = lat;
        }
    }

    if (sockfd >= 0) close(sockfd);
    return NULL;
}

int cmp(const void *a, const void *b) {
    double arg1 = *(const double *)a;
    double arg2 = *(const double *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

int main() {
    pthread_t threads[THREADS];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    for (int i = 0; i < THREADS; i++) {
        pthread_create(&threads[i], NULL, worker, NULL);
    }

    for (int i = 0; i < THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    clock_gettime(CLOCK_MONOTONIC_RAW, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    qsort(latencies, total_completed, sizeof(double), cmp);

    printf("\n================ BARE-METAL C BENCHMARK ================\n");
    printf("Total Requests : %d / %d\n", total_completed, TOTAL_REQUESTS);
    printf("Duration       : %.4f s\n", elapsed);
    printf("Throughput     : %.2f req/sec\n", total_completed / elapsed);
    if (total_completed > 0) {
        printf("Avg Latency    : %.3f ms\n", latencies[total_completed / 2]);
        printf("P50 Latency    : %.3f ms (%.1f us)\n", latencies[(int)(total_completed * 0.50)], latencies[(int)(total_completed * 0.50)] * 1000);
        printf("P99 Latency    : %.3f ms (%.1f us)\n", latencies[(int)(total_completed * 0.99)], latencies[(int)(total_completed * 0.99)] * 1000);
    }
    printf("========================================================\n\n");

    return 0;
}
