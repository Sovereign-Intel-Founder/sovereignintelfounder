#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>

int main() {
    uint64_t start, end;
    
    // Measure execution cycles with hardware timestamp counter
    start = __rdtsc();
    for(volatile int i = 0; i < 1000; i++);
    end = __rdtsc();
    
    printf("[+] RDTSC cycle-accurate telemetry captured.\n");
    printf("[+] Elapsed clock cycles: %lu\n", (end - start));
    return 0;
}
