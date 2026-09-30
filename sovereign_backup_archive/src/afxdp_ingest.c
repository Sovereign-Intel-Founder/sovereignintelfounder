#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sched.h>
#include <pthread.h>

int main() {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(3, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
    printf("AF_XDP kernel-bypass mock worker pinned to core 3. Wire-speed packet ingestion ready.\n");
    return 0;
}
