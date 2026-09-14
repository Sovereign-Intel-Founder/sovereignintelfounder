#define _GNU_SOURCE
#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

#define SHM_NAME "/sip_zero_alloc_ring"

int main() {
    int fd = shm_open(SHM_NAME, O_RDWR, 0666);
    void* ptr = mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    memcpy(ptr, "TICK:BTCUSD:68420.50:VOL:1.25", 30);
    printf("Live market feed tick ingested into shared memory ring buffer.\n");
    munmap(ptr, 4096);
    close(fd);
    return 0;
}
