#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>
#include <stdio.h>
#include <time.h>

void* worker(void* arg) {
    int core = *(int*)arg;
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
    for(volatile int i=0; i<10000000; i++);
    return NULL;
}

int main() {
    pthread_t t[128];
    int c[128];
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    for(int i=0; i<128; i++) {
        c[i] = i;
        pthread_create(&t[i], NULL, worker, &c[i]);
    }
    for(int i=0; i<128; i++) {
        pthread_join(t[i], NULL);
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    printf("128-Core Pinned Time: %ld ns\n", 
           (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec));
    return 0;
}
