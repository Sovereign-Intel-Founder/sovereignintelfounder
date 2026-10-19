#ifndef SIP_FLOW_H
#define SIP_FLOW_H

#define SIP_OPAQUE_TRUE(x) (((x) * (x) >= 0) && ((x) | 1))

#define SIP_OBFUSCATE_BLOCK(val, code_block) \
    do { \
        volatile uint64_t state = (uint64_t)(val); \
        state = (state ^ 0xDEADBEEFCAFEBABEULL) + 0x1337; \
        if (SIP_OPAQUE_TRUE((int)state)) { \
            code_block \
        } else { \
            volatile uint64_t dead = state * 31; \
            (void)dead; \
        } \
    } while(0)

#endif // SIP_FLOW_H
