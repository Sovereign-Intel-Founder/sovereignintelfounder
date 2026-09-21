#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdatomic.h>

typedef struct {
    char pad1[64];
    atomic_size_t head;
    char pad2[64];
    atomic_size_t tail;
    char pad3[64];
    uint64_t buffer[1024];
} LockFreeSPSCQueue;

int main() {
    LockFreeSPSCQueue q = {0};
    atomic_store(&q.tail, 42);
    printf("Lock-free SPSC queue initialized with atomic head/tail (Tail: %zu)\n", atomic_load(&q.tail));
    return 0;
}
