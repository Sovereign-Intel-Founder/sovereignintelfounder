#ifndef SOVEREIGN_MESH_INDEX_H
#define SOVEREIGN_MESH_INDEX_H

#include <stdint.h>
#include "test_live_stream.h"

typedef struct {
    uint64_t total_routed;
    uint64_t jito_bundles_triggered;
    uint64_t total_tips_lamports;
    uint64_t rolling_delta_sum;
    uint64_t relayer_dispatches;
    uint64_t route_buckets[8];
} mesh_router_t;

void init_mesh_router(mesh_router_t *router);
uint32_t route_mesh_frame_ultimate(mesh_router_t *router, const live_frame_t *frame, uint64_t current_tsc);

#endif
