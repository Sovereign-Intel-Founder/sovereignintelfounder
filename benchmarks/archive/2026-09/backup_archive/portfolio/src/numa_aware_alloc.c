#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <numa.h>
#include <numaif.h>

int main() {
    if (numa_available() < 0) {
        printf("[-] NUMA not supported on this system.\n");
        return 1;
    }

    int num_nodes = numa_max_node() + 1;
    printf("[+] NUMA Subsystem Initialized. Total Nodes Available: %d\n", num_nodes);

    // Allocate 2MB on NUMA node 0 strictly
    size_t alloc_size = 2 * 1024 * 1024;
    void *local_mem = numa_alloc_onnode(alloc_size, 0);
    if (!local_mem) {
        perror("numa_alloc_onnode failed");
        return 1;
    }

    printf("[+] Allocated %lu bytes strictly bound to NUMA node 0: %p\n", alloc_size, local_mem);

    numa_free(local_mem, alloc_size);
    printf("[+] NUMA-local memory cleanly released.\n");
    return 0;
}
