#ifndef SIP_FLOW_H
#define SIP_FLOW_H

// Opaque predicate macro: mathematically invariant at runtime, 
// but looks like unpredictable conditional branching to static disassemblers
#define SIP_OPAQUE_TRUE(x) (((x) * (x) >= 0))

#define SIP_OBFUSCATE_BLOCK(val, code_block) \
    do { \
        volatile int state = (val); \
        if (SIP_OPAQUE_TRUE(state)) { \
            code_block \
        } else { \
            volatile int dead_code = state ^ 0xDEADBEEF; \
            (void)dead_code; \
        } \
    } while(0)

#endif // SIP_FLOW_H
