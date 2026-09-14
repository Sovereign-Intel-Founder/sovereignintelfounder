#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define SHM_NAME "/edge_ai_tensor_weights"
#define TENSOR_SIZE (1024 * 1024 * 64) // 64 MB model weight block

int main() {
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd < 0) {
        perror("shm_open failed");
        return 1;
    }

    if (ftruncate(shm_fd, TENSOR_SIZE) != 0) {
        perror("ftruncate failed");
        return 1;
    }

    void *addr = mmap(NULL, TENSOR_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (addr == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    printf("[+] Edge AI zero-copy shared memory tensor region mapped successfully.\n");
    printf("[+] Allocated block size: %d MB at address %p\n", TENSOR_SIZE / (1024 * 1024), addr);

    munmap(addr, TENSOR_SIZE);
    close(shm_fd);
    shm_unlink(SHM_NAME);
    return 0;
}
