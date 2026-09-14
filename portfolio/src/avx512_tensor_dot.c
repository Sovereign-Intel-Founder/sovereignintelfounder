#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <immintrin.h>

float simd_dot_product_avx512(const float *a, const float *b, int n) {
    __m512 sum512 = _mm512_setzero_ps();
    int i;
    
    // Process 16 floats per iteration using 512-bit AVX registers
    for (i = 0; i <= n - 16; i += 16) {
        __m512 va = _mm512_loadu_ps(&a[i]);
        __m512 vb = _mm512_loadu_ps(&b[i]);
        sum512 = _mm512_fmadd_ps(va, vb, sum512);
    }
    
    // Horizontal sum of the 512-bit register
    float result = _mm512_reduce_add_ps(sum512);
    
    // Handle tail elements
    for (; i < n; i++) {
        result += a[i] * b[i];
    }
    
    return result;
}

int main() {
    int n = 1024;
    float *a = aligned_alloc(64, n * sizeof(float));
    float *b = aligned_alloc(64, n * sizeof(float));
    
    for (int i = 0; i < n; i++) {
        a[i] = 1.0f;
        b[i] = 2.0f;
    }

    float dot = simd_dot_product_avx512(a, b, n);
    
    printf("[+] AVX-512 SIMD tensor dot-product benchmark executed.\n");
    printf("[+] Vector Size: %d elements | Result: %.2f\n", n, dot);

    free(a);
    free(b);
    return 0;
}
