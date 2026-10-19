# Sovereign Intelligence Protocol - Systems Engineering Architecture

## Hardware & Environment Telemetry
* **Processor**: 128-core AMD EPYC with NUMA topology-aware core mapping.
* **Kernel**: Linux 6.x patched with `PREEMPT_RT` for deterministic low-latency response.
* **Network**: Dual 10GbE SFP+ interfaces leveraging `AF_XDP` kernel bypass.
* **Memory Architecture**: POSIX shared memory ring buffers (`/dev/shm`) and topology-bound allocations via `libnuma`.

## Core Subsystems
1. **Kernel-Bypass Ingestion (`afxdp_packet_capture.c`)**: Zero-copy packet capture directly from NIC rings into user space, circumventing the Linux networking stack.
2. **Topology-Aware Pinning (`numa_core_pin.c`)**: Explicit core isolation and NUMA node alignment to eliminate cross-socket memory bus latency penalties.
3. **Vectorized Matching Engine (`avx512_order_matcher.c`)**: Parallel evaluation of order book state via AVX-512 SIMD instruction sets, processing multiple price vectors per clock cycle.
4. **Zero-Allocation IPC (`zero_alloc_ipc.c`)**: Lock-free asynchronous message passing across processes via memory-mapped shared regions.
