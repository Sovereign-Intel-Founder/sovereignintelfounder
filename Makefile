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
