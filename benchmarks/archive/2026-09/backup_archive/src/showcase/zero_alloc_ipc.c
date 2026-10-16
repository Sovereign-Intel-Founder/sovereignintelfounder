#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

#define SHM_NAME "/sip_zero_alloc_ring"
#define SHM_SIZE 4096

int main() {
    int fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    ftruncate(fd, SHM_SIZE);
    void* ptr = mmap(0, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    
    strcpy((char*)ptr, "SOVEREIGN_INTELLIGENCE_PROTOCOL_ZERO_ALLOC_STREAM");
    printf("Zero-allocation POSIX shared memory IPC mapped at /dev/shm%s\n", SHM_NAME);
    
    munmap(ptr, SHM_SIZE);
    close(fd);
    return 0;
}
