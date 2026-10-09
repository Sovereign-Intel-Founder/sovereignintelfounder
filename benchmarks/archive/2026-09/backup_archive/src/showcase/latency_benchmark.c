#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>

int main() {
    unsigned int aux;
    uint64_t start = __rdtscp(&aux);
    for (volatile int i = 0; i < 1000; i++);
    uint64_t end = __rdtscp(&aux);
    
    printf("[+] High-resolution RDTSC tick-to-trade cycle probe active.\n");
    printf("[+] Elapsed cycles for 1,000 iterations: %lu cycles (~%lu cycles/op)\n", 
           (end - start), (end - start) / 1000);
    return 0;
}
