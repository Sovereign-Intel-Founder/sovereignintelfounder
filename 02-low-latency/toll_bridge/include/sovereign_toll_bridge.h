#ifndef SOVEREIGN_TOLL_BRIDGE_H
#define SOVEREIGN_TOLL_BRIDGE_H

#include <stdint.h>
#include "test_live_stream.h"

int validate_toll_bridge_frame(const live_frame_t *frame);
int validate_toll_bridge_vectorized(const live_frame_t *frames, int count);

#endif
