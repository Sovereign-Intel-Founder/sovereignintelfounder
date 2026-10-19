#ifndef SIP_STR_H
#define SIP_STR_H

#include <string.h>

// Simple XOR compile-time/runtime stack string obfuscator macro
#define SIP_OBF_KEY 0xAA

// Helper to decrypt strings on the stack dynamically
static inline void sip_reveal(char *dest, const char *src, size_t len) {
    for (size_t i = 0; i < len; i++) {
        dest[i] = src[i] ^ SIP_OBF_KEY;
    }
    dest[len] = '\0';
}

#endif // SIP_STR_H
