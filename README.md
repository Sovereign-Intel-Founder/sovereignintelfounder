# High-Performance Systems & Infrastructure Portfolio

Production-grade systems engineering portfolio focusing on kernel-level optimizations, low-latency network bypass, and extreme concurrency models. Built and validated on dedicated bare-metal infrastructure (128-Core AMD EPYC, PREEMPT_RT Linux kernel).

## Core Competencies & Architecture
* **Network Kernel Bypass**: Direct `AF_XDP` packet ingestion bypassing standard OS network stacks to eliminate packet drop under high-throughput burst loads.
* **Concurrency & Lock-Free IPC**: Lock-free single-producer single-consumer ring buffers (`SPSC`) and zero-copy POSIX shared memory inter-process communication.
* **NUMA-Aware Memory Management**: Rigorous CPU core pinning and memory allocation mapped to physical NUMA nodes to minimize cross-socket memory latency.
* **Deterministic Execution**: `PREEMPT_RT` kernel telemetry and high-precision TSC (Time-Stamp Counter) timing validation for sub-microsecond tracing.

## Repository Layout
* `portfolio/src/` - Canonical low-latency C systems primitives, memory allocators, and networking drivers.
* `PORTFOLIO_MAP.md` - Complete architectural index for technical reviewers and hiring managers.
* `SECURITY.md` - Repository hygiene, data scrubbing, and credential isolation standards.
* `coliseum-submission/` - Archived historical competition records and domain-specific test harnesses.
