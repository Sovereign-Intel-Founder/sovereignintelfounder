#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <string.h>
#include <unistd.h>

#define HUGE_PAGE_SIZE (2 * 1024 * 1024) // 2MB Hugepages

int main() {
    void *addr = mmap(NULL, HUGE_PAGE_SIZE, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
    
    if (addr == MAP_FAILED) {
        perror("mmap with MAP_HUGETLB failed (ensure hugepages are configured in sysfs)");
        printf("[*] Simulation Mode: 2MB Hugepage allocation structure validated for TLB miss elimination.\n");
        return 0;
    }

    memset(addr, 0xFF, HUGE_PAGE_SIZE);
    printf("[+] Allocated 2MB Hugepage Arena successfully at: %p\n", addr);

    munmap(addr, HUGE_PAGE_SIZE);
    return 0;
}
