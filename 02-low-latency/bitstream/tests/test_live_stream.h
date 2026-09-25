#ifndef TEST_LIVE_STREAM_H
#define TEST_LIVE_STREAM_H

#include <stdint.h>

#define SHM_NAME "/sovereign_live_ring"
#define RING_CAPACITY 131072 
#define SHM_SIZE (sizeof(shared_ring_t))

typedef struct {
    uint64_t sequence_id;
    uint64_t capture_tsc; // Hardware cycle timestamp captured at wire ingestion
    uint32_t payload_length;
    uint32_t flags;
    uint8_t data[239];
} __attribute__((packed)) live_frame_t;

typedef struct __attribute__((aligned(64))) {
    volatile uint64_t head __attribute__((aligned(64)));
    volatile uint64_t tail __attribute__((aligned(64)));
    live_frame_t frames[RING_CAPACITY];
} shared_ring_t;

#endif
