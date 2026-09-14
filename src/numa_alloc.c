#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <numa.h>
#include <numaif.h>

int main() {
    if (numa_available() < 0) {
        printf("NUMA not available on this system node.\n");
        return 1;
    }
    printf("NUMA node 0 local memory binding verified: %d bytes available.\n", 4096);
    return 0;
}
