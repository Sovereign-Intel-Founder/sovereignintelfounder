# Systems Engineering Portfolio Map

This repository showcases low-latency C primitives, concurrency models, and hardware optimization prototypes.

## Component Index & Status
* **AF_XDP Packet Bypass**: `portfolio/src/af_xdp_packet_bypass.c` (Status: Socket-level prototype / probe)
* **Lock-Free SPSC Ring**: `portfolio/src/lockfree_spsc_ring.c` (Status: Atomic concurrency primitive)
* **NUMA Allocation & Core Pinning**: `portfolio/src/numa_aware_alloc.c`, `portfolio/src/numa_core_pin.c` (Status: Hardware topology API demonstrations)
* **Latency & RDTSC Telemetry**: `portfolio/src/latency_benchmark.c`, `portfolio/src/rdtsc_telemetry.c` (Status: Cycle-counter measurement probes)

## Evidence & Reproducibility
* Archived competition materials remain isolated in `coliseum-submission/`.
* Build and test execution details for individual primitives are documented alongside source modules.
