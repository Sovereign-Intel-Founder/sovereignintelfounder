#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <time.h>
int main() {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    sched_setaffinity(0, sizeof(cpuset), &cpuset);
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    for(volatile int i=0; i<10000000; i++);
    clock_gettime(CLOCK_MONOTONIC, &end);
    printf("Pinned Core Latency: %ld ns\n", (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec));
    return 0;
}
