#ifndef SOVEREIGN_BITSTREAM_H
#define SOVEREIGN_BITSTREAM_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define CACHE_LINE_SIZE 64
#define RING_BUFFER_MASK 0xFFFF // 64K slots
#define BITSTREAM_MAX_PAYLOAD 1024

// 64-byte cache-line aligned frame structure for zero-copy transport
typedef struct __attribute__((aligned(CACHE_LINE_SIZE))) {
    uint64_t timestamp_cycles;
    uint32_t flow_signature;
    uint16_t payload_length;
    uint16_t flags;
    uint8_t  data[BITSTREAM_MAX_PAYLOAD];
    uint8_t  padding[32]; // Padding to ensure strict cache-line alignment
} BitstreamFrame;

// Lock-free SPSC Ring Buffer backed by POSIX Shared Memory
typedef struct __attribute__((aligned(CACHE_LINE_SIZE))) {
    volatile uint64_t head;
    char pad1[CACHE_LINE_SIZE - sizeof(uint64_t)];
    volatile uint64_t tail;
    char pad2[CACHE_LINE_SIZE - sizeof(uint64_t)];
    BitstreamFrame frames[RING_BUFFER_MASK + 1];
} BitstreamRingBuffer;

// Function Prototypes
int bitstream_ring_init(BitstreamRingBuffer *ring);
bool bitstream_enqueue(BitstreamRingBuffer *ring, const uint8_t *data, uint16_t length, uint32_t signature);
bool bitstream_dequeue(BitstreamRingBuffer *ring, BitstreamFrame *out_frame);

#endif // SOVEREIGN_BITSTREAM_H
