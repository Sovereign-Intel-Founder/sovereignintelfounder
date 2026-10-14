#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "sip_str.h"
#include "sip_flow.h"
#include "sip_sentinel.h"

uint64_t compute_secure_token(uint64_t seed) {
    volatile uint64_t accumulator = seed ^ 0x5A5A5A5A33333333ULL;
    volatile int state = 3;
    
    while (state != 0) {
        switch (state) {
            case 3:
                accumulator = (accumulator << 3) | (accumulator >> 61);
                state = 1;
                break;
            case 1:
                accumulator ^= (seed + 0x1337);
                state = 2;
                break;
            case 2:
                accumulator = ~accumulator;
                state = 0;
                break;
            default:
                state = 0;
                break;
        }
    }
    return accumulator;
}
