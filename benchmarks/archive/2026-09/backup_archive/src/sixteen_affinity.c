#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>
#include <stdio.h>
#include <time.h>

void* worker(void* arg) {
    int core_id = *(int*)arg;
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
    for(volatile int i=0; i<10000000; i++);
    return NULL;
}

int main() {
    pthread_t threads[16];
    int cores[16];
    struct timespec start, end;
    
    clock_gettime(CLOCK_MONOTONIC, &start);
    for(int i=0; i<16; i++) {
        cores[i] = i;
        pthread_create(&threads[i], NULL, worker, &cores[i]);
    }
    for(int i=0; i<16; i++) pthread_join(threads[i], NULL);
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    printf("16-Core Pinned Time: %ld ns\n", 
           (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec));
    return 0;
}
