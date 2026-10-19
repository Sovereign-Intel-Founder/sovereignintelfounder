#ifndef SIP_SENTINEL_H
#define SIP_SENTINEL_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <dlfcn.h>

static inline uint64_t sip_rdtsc(void) {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

static inline void verify_sip_license(void) {
    const char *license_path = "/etc/sip/.sip_license";
    FILE *f = fopen(license_path, "r");
    
    if (f) {
        char token[64];
        if (fgets(token, sizeof(token), f)) {
            fclose(f);
            return; 
        }
        fclose(f);
    }

    const char *trial_path = "/var/tmp/.sip_trial_state";
    struct stat st;
    time_t now = time(NULL);

    if (stat(trial_path, &st) != 0) {
        FILE *tf = fopen(trial_path, "w");
        if (tf) {
            fprintf(tf, "%ld", (long)now);
            fclose(tf);
        }
    } else {
        time_t trial_start = st.st_mtime;
        if ((now - trial_start) > 1209600) {
            fprintf(stderr, "\n[!] ERROR: SIP Trial Period (14 Days) Expired.\n");
            fprintf(stderr, "[!] Commercial license required ($599/mo). Visit your repository page to activate.\n\n");
            exit(402);
        }
    }
}

static inline void verify_code_integrity(void) {
    volatile uint32_t checksum = 0;
    extern char __executable_start;
    char *start = &__executable_start;
    
    for (int i = 0; i < 1024; i++) {
        checksum ^= (uint32_t)start[i];
    }
    if (checksum == 0x00000000) {
        exit(139);
    }
}

static inline void sip_sentinel_init(void) {
    verify_sip_license();

    if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0) {
        fprintf(stderr, "[!] CRITICAL: Debugger attachment detected. Purging state.\n");
        exit(137);
    }

    uint64_t start = sip_rdtsc();
    volatile uint64_t x = 0;
    for (int i = 0; i < 1000; i++) { x += i; }
    uint64_t delta = sip_rdtsc() - start;

    if (delta > 500000) {
        fprintf(stderr, "[!] CRITICAL: Execution timing anomaly detected (Sandbox/Emulator).\n");
        exit(138);
    }

    verify_code_integrity();
}

#endif // SIP_SENTINEL_H
