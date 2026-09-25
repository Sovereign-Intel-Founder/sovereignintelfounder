#include "sovereign_bitstream.h"
#include <string.h>
#include <x86intrin.h>

int bitstream_ring_init(BitstreamRingBuffer *ring) {
    if (!ring) return -1;
    ring->head = 0;
    ring->tail = 0;
    memset(ring->frames, 0, sizeof(ring->frames));
    return 0;
}

bool bitstream_enqueue(BitstreamRingBuffer *ring, const uint8_t *data, uint16_t length, uint32_t signature) {
    if (length > BITSTREAM_MAX_PAYLOAD) return false;

    uint64_t head = __atomic_load_n(&ring->head, __ATOMIC_RELAXED);
    uint64_t tail = __atomic_load_n(&ring->tail, __ATOMIC_ACQUIRE);

    if ((head - tail) > RING_BUFFER_MASK) {
        return false; // Ring buffer full
    }

    BitstreamFrame *frame = &ring->frames[head & RING_BUFFER_MASK];
    
    // Zero-copy inline projection using AVX/SSE alignment
    frame->timestamp_cycles = __rdtsc();
    frame->flow_signature = signature;
    frame->payload_length = length;
    frame->flags = 0x01; // Polymorphic active state

    // Fast memory copy mapped directly to frame payload buffer
    memcpy(frame->data, data, length);

    __atomic_store_n(&ring->head, head + 1, __ATOMIC_RELEASE);
    return true;
}

bool bitstream_dequeue(BitstreamRingBuffer *ring, BitstreamFrame *out_frame) {
    uint64_t tail = __atomic_load_n(&ring->tail, __ATOMIC_RELAXED);
    uint64_t head = __atomic_load_n(&ring->head, __ATOMIC_ACQUIRE);

    if (tail == head) {
        return false; // Ring buffer empty
    }

    BitstreamFrame *frame = &ring->frames[tail & RING_BUFFER_MASK];
    
    // Copy out structured frame data
    *out_frame = *frame;

    __atomic_store_n(&ring->tail, tail + 1, __ATOMIC_RELEASE);
    return true;
}
