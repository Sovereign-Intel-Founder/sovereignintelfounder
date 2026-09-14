# Systems Engineering Portfolio Map

This repository showcases advanced, low-latency systems engineering, high-throughput concurrency models, and Linux kernel optimization. 

## Canonical Architecture Path
* **Network Kernel Bypass**: `portfolio/src/af_xdp_packet_bypass.c` - Direct high-speed network packet ingress bypassing the standard Linux network stack.
* **Concurrency & Memory**: `portfolio/src/lockfree_spsc_ring.c` & `portfolio/src/shm_ipc_ring.c` - Lock-free single-producer single-consumer ring buffers and POSIX shared memory IPC.
* **Hardware & CPU Affinity**: `portfolio/src/numa_aware_alloc.c` & `portfolio/src/numa_core_pin.c` - NUMA-aware memory allocation and rigorous core pinning to eliminate cross-socket memory latency.
* **Telemetry & Benchmarking**: `portfolio/src/latency_benchmark.c` & `portfolio/src/rdtsc_telemetry.c` - Microsecond-scale precision execution tracing using CPU time-stamp counters.
