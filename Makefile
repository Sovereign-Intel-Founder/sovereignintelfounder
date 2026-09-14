CC = gcc
CFLAGS = -O3 -Wall -Wextra -pthread

showcase_all: afxdp_packet_capture numa_core_pin avx512_order_matcher zero_alloc_ipc

afxdp_packet_capture: src/showcase/afxdp_packet_capture.c
	$(CC) $(CFLAGS) $< -o $@

numa_core_pin: src/showcase/numa_core_pin.c
	$(CC) $(CFLAGS) $< -o $@ -lnuma -lpthread

avx512_order_matcher: src/showcase/avx512_order_matcher.c
	$(CC) -O3 -mavx512f $< -o $@

zero_alloc_ipc: src/showcase/zero_alloc_ipc.c
	$(CC) $(CFLAGS) $< -o $@ -lrt

clean:
	rm -f afxdp_packet_capture numa_core_pin avx512_order_matcher zero_alloc_ipc

spsc_ring: src/showcase/spsc_ring.c
	$(CC) $(CFLAGS) $< -o $@

ebpf_loader: src/showcase/ebpf_loader.c
	$(CC) $(CFLAGS) $< -o $@

market_feed_ingest: src/showcase/market_feed_ingest.c
	$(CC) $(CFLAGS) $< -o $@ -lrt

ptp_hardware_timestamp: src/showcase/ptp_hardware_timestamp.c
	$(CC) $(CFLAGS) $< -o $@

xdp_driver_hook: src/showcase/xdp_driver_hook.c
	$(CC) $(CFLAGS) $< -o $@

latency_benchmark: src/showcase/latency_benchmark.c
	$(CC) $(CFLAGS) $< -o $@

lockfree_spsc_ring: src/showcase/lockfree_spsc_ring.c
	$(CC) $(CFLAGS) $< -o $@

numa_pinning: src/showcase/numa_pinning.c
	$(CC) $(CFLAGS) $< -o $@

ptp_hardware_timestamp: src/showcase/ptp_hardware_timestamp.c
	$(CC) $(CFLAGS) $< -o $@

rdtsc_telemetry: src/showcase/rdtsc_telemetry.c
	$(CC) $(CFLAGS) $< -o $@

edge_ai_tensor_map: src/showcase/edge_ai_tensor_map.c
	$(CC) $(CFLAGS) $< -o $@ -lrt

avx512_tensor_dot: src/showcase/avx512_tensor_dot.c
	$(CC) $(CFLAGS) -mavx512f -mavx512cd $< -o $@

edge_ai_inference: src/showcase/edge_ai_inference.c
	$(CC) $(CFLAGS) -mavx512f -mavx512cd $< -o $@ -lrt

lockfree_memory_pool: src/showcase/lockfree_memory_pool.c
	$(CC) $(CFLAGS) $< -o $@

af_xdp_packet_bypass: src/showcase/af_xdp_packet_bypass.c
	$(CC) $(CFLAGS) $< -o $@

shm_ipc_ring: src/showcase/shm_ipc_ring.c
	$(CC) $(CFLAGS) -lrt $< -o $@

hardware_perf_counters: src/showcase/hardware_perf_counters.c
	$(CC) $(CFLAGS) $< -o $@

udp_consensus_heartbeat: src/showcase/udp_consensus_heartbeat.c
	$(CC) $(CFLAGS) $< -o $@
