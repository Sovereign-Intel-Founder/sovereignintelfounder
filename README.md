# Bare-Metal High-Concurrency Mesh Engine

A high-throughput, low-latency asynchronous message routing engine built to maximize bare-metal performance on multi-socket Linux systems.

## Key Hardware Benchmarks (128 Cores / 728 GB RAM)

| Benchmark Metric | Measured Result | Methodology / Hardware Isolation |
| :--- | :--- | :--- |
| **Peak Multi-Core Bandwidth** | **72.27 GB/sec** (68,919 MiB/s) | 128-thread parallel memory saturation across all NUMA domains |
| **Local Memory Throughput** | **20.84 GB/sec** | Single-threaded `memcpy` on NUMA Node 0 |
| **Cross-Socket Memory Read** | **13.48 GB/sec** | Single-threaded unpinned read across interconnect socket |
| **NUMA Interconnect Penalty** | **35.31% Penalty** | 1 - (13.48 / 20.84) * 100 |
| **Context Switch Throughput** | **166,901 ops/sec** | `perf bench sched pipe` under `performance` CPU governor |
| **Scheduling Latency** | **~5.99 µs / operation** | Microsecond thread execution baseline |

## Systems Architecture & Topology

* **Ingestion Gateway**: Asyncio zero-queue ingress loop.
* **NUMA Node 0**: 64 Cores / 384 GB RAM (Worker Threads).
* **NUMA Node 1**: 64 Cores / 384 GB RAM (Worker Threads).
* **Thread Pinning**: CPU affinity enforced via `numactl` to eliminate cross-socket L1/L2/L3 cache misses.
* **Low-Latency Tuning**: CPU governor locked to `performance`, deep C-states disabled to prevent microsecond wake-up jitter.

## Repository Structure
* `docs/ARCHITECTURE.md` - System topology, lockless queueing, and thread affinity model.
* `docs/CASE_STUDY.md` - Executive summary of bare-metal optimization results.
* `benchmarks/BENCHMARKS.md` - Mathematical proofs, raw metrics, and NUMA penalty calculations.
* `benchmarks/cpu_flamegraph_profile.txt` - `perf` CPU stack trace analysis.
* `scripts/ci_bench.sh` - Automated CI regression testing harness.
