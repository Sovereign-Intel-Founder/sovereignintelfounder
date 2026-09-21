# Systems Engineering Portfolio Map & Navigation

This repository serves a dual purpose: preserving the active Sovereign Intelligence Protocol (SIP) systems entry and showcasing standalone systems-engineering primitives developed during its research.

## Navigation & Architecture
* **Standalone C Primitives**: `portfolio/src/` (Low-latency networking probes, lock-free structures, NUMA-aware allocation, and telemetry tools).

## Component Index
* **AF_XDP Packet Bypass**: `portfolio/src/af_xdp_packet_bypass.c` (Socket-level probe)
* **Lock-Free SPSC Ring**: `portfolio/src/lockfree_spsc_ring.c` (Atomic concurrency primitive)
* **NUMA Allocation & Core Pinning**: `portfolio/src/numa_aware_alloc.c`, `portfolio/src/numa_core_pin.c` (Hardware topology API demonstrations)
* **Latency & RDTSC Telemetry**: `portfolio/src/latency_benchmark.c`, `portfolio/src/rdtsc_telemetry.c` (Cycle-counter measurement probes)
