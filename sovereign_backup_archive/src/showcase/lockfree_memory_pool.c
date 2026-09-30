#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <stdatomic.h>

#define POOL_SIZE (1024 * 1024 * 64) // 64 MB Arena
#define BLOCK_SIZE 64                // Cache-line aligned blocks

typedef struct block_node {
    _Atomic(struct block_node *) next;
} block_node_t;

typedef struct {
    void *arena;
    _Atomic(block_node_t *) head;
} lockfree_pool_t;

lockfree_pool_t *pool_create() {
    lockfree_pool_t *pool = malloc(sizeof(lockfree_pool_t));
    pool->arena = mmap(NULL, POOL_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
    if (pool->arena == MAP_FAILED) {
        // Fallback if hugepages are not configured
        pool->arena = mmap(NULL, POOL_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    }

    block_node_t *first = (block_node_t *)pool->arena;
    size_t num_blocks = POOL_SIZE / BLOCK_SIZE;

    for (size_t i = 0; i < num_blocks - 1; i++) {
        block_node_t *curr = (block_node_t *)((char *)pool->arena + (i * BLOCK_SIZE));
        block_node_t *next = (block_node_t *)((char *)pool->arena + ((i + 1) * BLOCK_SIZE));
        atomic_init(&curr->next, next);
    }
    block_node_t *last = (block_node_t *)((char *)pool->arena + ((num_blocks - 1) * BLOCK_SIZE));
    atomic_init(&last->next, NULL);

    atomic_init(&pool->head, first);
    return pool;
}

void *pool_alloc(lockfree_pool_t *pool) {
    block_node_t *old_head;
    do {
        old_head = atomic_load(&pool->head);
        if (old_head == NULL) return NULL;
    } while (!atomic_compare_exchange_weak(&pool->head, &old_head, atomic_load(&old_head->next)));
    return (void *)old_head;
}

void pool_free(lockfree_pool_t *pool, void *ptr) {
    block_node_t *node = (block_node_t *)ptr;
    block_node_t *old_head;
    do {
        old_head = atomic_load(&pool->head);
        atomic_store(&node->next, old_head);
    } while (!atomic_compare_exchange_weak(&pool->head, &old_head, node));
}

int main() {
    lockfree_pool_t *pool = pool_create();
    
    void *mem1 = pool_alloc(pool);
    void *mem2 = pool_alloc(pool);
    
    printf("[+] Lock-free memory pool initialized via mmap.\n");
    printf("[+] Allocated block 1: %p\n", mem1);
    printf("[+] Allocated block 2: %p\n", mem2);

    pool_free(pool, mem1);
    pool_free(pool, mem2);

    munmap(pool->arena, POOL_SIZE);
    free(pool);
    printf("[+] Arena cleanly destroyed with zero memory leaks.\n");
    return 0;
}
