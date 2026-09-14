# High-Performance Systems & Infrastructure Portfolio

Systems engineering portfolio focusing on low-latency C primitives, concurrency structures, NUMA-aware allocation, and telemetry probes. Developed and tested on bare-metal infrastructure (128-core AMD EPYC, PREEMPT_RT Linux kernel).

## Core Components & Architecture
* **AF_XDP Socket Probe**: Socket-level packet bypass prototype exploring direct ring-buffer packet ingestion.
* **Lock-Free SPSC Ring**: Atomic single-producer single-consumer ring buffer implementation demonstrating lock-free concurrency.
* **NUMA-Aware Memory**: Primitives and core-pinning utilities for local node memory allocation and thread affinity mapping.
* **Telemetry Probes**: High-precision cycle counter (`RDTSC`) and benchmarking probes for execution tracing.

## Repository Structure
* `portfolio/src/` - Standalone C systems primitives, memory allocators, and networking probes.
* `PORTFOLIO_MAP.md` - Technical index mapping showcase files to their implementation status.
* `SECURITY.md` - Repository hygiene, data scrubbing, and security standards.
* `coliseum-submission/` - Archived historical competition records and domain-specific test harnesses.
