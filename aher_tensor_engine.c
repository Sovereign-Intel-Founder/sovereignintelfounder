#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <immintrin.h>

#define TENSOR_STREAM_SIZE (512 * 1024 * 1024UL) // 512 MB
#define VECTOR_WIDTH       64                    // 64-byte cache line alignment
#define MAX_CORES          128

typedef struct {
    uint64_t lane_signature;
    uint64_t phase_vector[7];
} __attribute__((aligned(VECTOR_WIDTH))) tensor_node_t;

typedef struct {
    int core_id;
    int total_cores;
    tensor_node_t* tensor_stream;
    size_t total_nodes;
    unsigned long tensors_projected;
} aher_context_t;

static inline void pin_to_physical_core(int core_id) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core_id % sysconf(_SC_NPROCESSORS_ONLN), &set);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &set);
}

void* aher_tensor_worker(void* arg) {
    aher_context_t* ctx = (aher_context_t*)arg;
    pin_to_physical_core(ctx->core_id);

    size_t slice_size = ctx->total_nodes / ctx->total_cores;
    size_t start_idx = ctx->core_id * slice_size;
    size_t end_idx = (ctx->core_id == ctx->total_cores - 1) ? ctx->total_nodes : start_idx + slice_size;

    unsigned long projected = 0;
    __m512i base_mask = _mm512_set1_epi64(ctx->core_id ^ 0x9E3779B97F4A7C15UL);

    for (size_t i = start_idx; i < end_idx; i++) {
        tensor_node_t* node = &ctx->tensor_stream[i];

        __m512i v_state = _mm512_set_epi64(
            (long long)i, (long long)ctx->core_id, (long long)(i ^ 0xFF), (long long)~i, 
            (long long)(ctx->core_id + i), 0x4250495345564552LL, 0x0123456789ABCDEFLL, 0x1337C0DE42424242LL
        );

        __m512i v_folded = _mm512_xor_si512(v_state, base_mask);
        
        // Use standard aligned store instead of non-temporal hint to guarantee safety across all EPYC cache lines
        _mm512_store_si512((void*)&node->lane_signature, _mm512_and_si512(v_folded, base_mask));
        _mm512_store_si512((void*)node->phase_vector, v_folded);

        projected++;
    }

    ctx->tensors_projected = projected;
    return NULL;
}

int main(int argc, char* argv[]) {
    int active_cores = MAX_CORES;
    if (argc > 1) {
        active_cores = atoi(argv[1]);
        if (active_cores <= 0 || active_cores > MAX_CORES) active_cores = MAX_CORES;
    }

    printf("============================================================\n");
    printf("   AHER : ASYNCHRONOUS HOLOGRAPHIC ENTANGLEMENT ENGINE       \n");
    printf("============================================================\n");

    size_t total_nodes = TENSOR_STREAM_SIZE / sizeof(tensor_node_t);
    size_t allocation_size = total_nodes * sizeof(tensor_node_t);

    // Strict 64-byte alignment allocation for AVX-512 safety
    tensor_node_t* tensor_stream = NULL;
    if (posix_memalign((void**)&tensor_stream, 64, allocation_size) != 0) {
        perror("posix_memalign failed");
        exit(1);
    }

    pthread_t threads[MAX_CORES];
    aher_context_t contexts[MAX_CORES];

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < active_cores; i++) {
        contexts[i].core_id = i;
        contexts[i].total_cores = active_cores;
        contexts[i].tensor_stream = tensor_stream;
        contexts[i].total_nodes = total_nodes;
        contexts[i].tensors_projected = 0;
        pthread_create(&threads[i], NULL, aher_tensor_worker, &contexts[i]);
    }

    unsigned long total_projected = 0;
    for (int i = 0; i < active_cores; i++) {
        pthread_join(threads[i], NULL);
        total_projected += contexts[i].tensors_projected;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    double velocity = total_projected / elapsed;

    printf("[-] AHER Execution Complete:\n");
    printf("    -> Tensors Projected       : %lu\n", total_projected);
    printf("    -> Elapsed Time            : %.6f seconds\n", elapsed);
    printf("    -> Entanglement Velocity   : %.2f ops/sec\n", velocity);
    printf("============================================================\n");

    free(tensor_stream);
    return 0;
}
