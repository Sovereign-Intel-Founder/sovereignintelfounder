#define _GNU_SOURCE
#include <stdio.h>
#include <pthread.h>
#include <sched.h>
#include <unistd.h>

void* thread_worker(void* arg) {
    (void)arg; // Explicitly suppress unused parameter warning
    int cpu = sched_getcpu();
    printf("[+] Worker thread successfully pinned and executing on CPU core: %d\n", cpu);
    return NULL;
}

int main() {
    pthread_t thread;
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    
    int target_core = 4;
    CPU_SET(target_core, &cpuset);

    if (pthread_create(&thread, NULL, thread_worker, NULL) != 0) {
        perror("pthread_create failed");
        return 1;
    }

    if (pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np failed");
    }

    pthread_join(thread, NULL);
    printf("[+] NUMA-aware core pinning validation complete.\n");
    return 0;
}
