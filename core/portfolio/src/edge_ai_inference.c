#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <immintrin.h>

#define SHM_NAME "/edge_ai_tensor_weights"
#define VECTOR_SIZE 1024

float forward_layer(const float *weights, const float *input, int n) {
    __m512 sum512 = _mm512_setzero_ps();
    int i;
    
    for (i = 0; i <= n - 16; i += 16) {
        __m512 va = _mm512_loadu_ps(&weights[i]);
        __m512 vb = _mm512_loadu_ps(&input[i]);
        sum512 = _mm512_fmadd_ps(va, vb, sum512);
    }
    
    float result = _mm512_reduce_add_ps(sum512);
    
    for (; i < n; i++) {
        result += weights[i] * input[i];
    }
    
    return result;
}

int main() {
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd < 0) {
        perror("shm_open failed");
        return 1;
    }
    
    if (ftruncate(shm_fd, VECTOR_SIZE * sizeof(float)) != 0) {
        perror("ftruncate failed");
        return 1;
    }

    float *weights = mmap(NULL, VECTOR_SIZE * sizeof(float), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (weights == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    for (int i = 0; i < VECTOR_SIZE; i++) {
        weights[i] = 0.5f;
    }

    float *input = aligned_alloc(64, VECTOR_SIZE * sizeof(float));
    for (int i = 0; i < VECTOR_SIZE; i++) {
        input[i] = 1.0f;
    }

    float output = forward_layer(weights, input, VECTOR_SIZE);
    
    printf("[+] Real zero-copy edge AI layer forward pass executed.\n");
    printf("[+] Vector Size: %d | Output Inference Value: %.2f\n", VECTOR_SIZE, output);

    munmap(weights, VECTOR_SIZE * sizeof(float));
    close(shm_fd);
    shm_unlink(SHM_NAME);
    free(input);
    return 0;
}
