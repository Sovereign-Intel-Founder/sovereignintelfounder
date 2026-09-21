# Sovereign Intelligence Protocol — Systems Engineering & Low-Latency Primitives

A high-performance systems engineering portfolio demonstrating low-latency IPC, custom ring buffers, POSIX shared memory zero-copy mechanisms, and rigorous bare-metal concurrency test harnesses.

## Repository Architecture

* `sip_core/` — Core protocol runtime and low-latency execution flow.
* `mesh/` — Mesh networking architecture and high-throughput event routing layers.
* `tollbridge_system/` — Toll bridge architecture, concurrency handlers, and gate logic.
* `portfolio/` — Standalone low-latency C primitives, ring buffers, and hardware-optimization research components.
* `simd/` — SIMD and vectorization research primitives.
* `solana-ledger/` — Ledger integration and RPC interface components.
* `scripts/` — Execution wrappers, stress test harnesses, and validation pipelines.
* `telemetry/` — Raw machine telemetry sweeps, stress logs, and JSON metrics.
* `docs/` — Deep-dive architecture specs, data matrices, and performance case studies.

## Verified Benchmarks & Telemetry

Tested on dedicated bare-metal infrastructure (128-core AMD EPYC, PREEMPT_RT Linux kernel, dual 10GbE SFP+):
* **Multi-Core Compute Saturation:** 2,787,589.29 ops/sec (`sip_core` SPSC pipeline).
* **Ring Buffer Latency:** ~8.15 ns per operation via zero-copy memory mapping.
* **Network Concurrency Stress:** 1,121.84 req/sec across 256 concurrent heavy multi-vector workers with 100% success rate.

See [RAW_MATRIX.md](RAW_MATRIX.md) and [BENCHMARKS.md](BENCHMARKS.md) for full execution telemetry and verification harnesses.
