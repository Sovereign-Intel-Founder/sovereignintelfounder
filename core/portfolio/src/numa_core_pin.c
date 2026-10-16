#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sched.h>
#include <numa.h>

void* worker_thread(void* arg) {
    int core_id = *(int*)arg;
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    int node = numa_node_of_cpu(core_id);
    printf("Worker thread pinned to core %d on NUMA node %d\n", core_id, node);
    return NULL;
}

int main() {
    pthread_t thread;
    int core = 64;
    pthread_create(&thread, NULL, worker_thread, &core);
    pthread_join(thread, NULL);
    return 0;
}
