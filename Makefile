
compile-spsc:
	@if [ -d "toll_gate" ]; then \
		$(MAKE) -C toll_gate compile-spsc 2>/dev/null || gcc -O3 -o spsc_ring_buffer benchmarks/ultra_metal_benchmark.c; \
	else \
		gcc -O3 -o spsc_ring_buffer benchmarks/ultra_metal_benchmark.c; \
	fi
