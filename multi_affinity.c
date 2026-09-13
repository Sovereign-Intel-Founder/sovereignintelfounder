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
    pthread_t t1, t2;
    int c1 = 0, c2 = 1;
    struct timespec start, end;
    
    clock_gettime(CLOCK_MONOTONIC, &start);
    pthread_create(&t1, NULL, worker, &c1);
    pthread_create(&t2, NULL, worker, &c2);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    printf("Multi-Core Pinned Time: %ld ns\n", 
           (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec));
    return 0;
}
