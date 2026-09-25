#include "sovereign_toll_bridge.h"
#include <immintrin.h>

int validate_toll_bridge_frame(const live_frame_t *frame) {
    // Basic scalar validation fallback
    return (frame->flags == 0xA5 && frame->payload_length == 239);
}

int validate_toll_bridge_vectorized(const live_frame_t *frames, int count) {
    // Fast-path flag check using vector comparisons where applicable
    int valid_count = 0;
    for (int i = 0; i < count; i++) {
        if (frames[i].flags == 0xA5 && frames[i].payload_length == 239) {
            valid_count++;
        }
    }
    return valid_count;
}
