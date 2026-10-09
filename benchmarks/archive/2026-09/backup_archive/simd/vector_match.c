#include <stdio.h>
#include <immintrin.h>

int main() {
    __m512i prices = _mm512_set1_epi64(100);
    __m512i threshold = _mm512_set1_epi64(95);
    __mmask8 mask = _mm512_cmp_epi64_mask(prices, threshold, _MM_CMPINT_LE);
    printf("AVX-512 vector price comparison mask: 0x%x\n", mask);
    return 0;
}
