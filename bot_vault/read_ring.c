#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

typedef struct {
    uint16_t opcode;
    uint16_t numa_target;
    uint64_t mem_pointer;
    uint32_t crypto_hash;
} __attribute__((packed)) BinaryInstruction;

int main() {
    int shm_fd = shm_open("/sip_ring_buffer", O_RDONLY, 0666);
    if (shm_fd == -1) { perror("shm_open failed"); return 1; }

    BinaryInstruction *ring = mmap(0, 1048576, PROT_READ, MAP_SHARED, shm_fd, 0);
    if (ring == MAP_FAILED) { perror("mmap failed"); return 1; }

    printf("Inspecting /sip_ring_buffer slots:\n");
    for (int i = 0; i < 4; i++) {
        printf("[%d] opcode: 0x%04x | numa: %u | mem_ptr: 0x%016llx | hash: 0x%08x\n",
               i, ring[i].opcode, ring[i].numa_target, 
               (unsigned long long)ring[i].mem_pointer, ring[i].crypto_hash);
    }
    return 0;
}
