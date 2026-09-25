# Benchmark Index & Evidence Ledger

All benchmarks are derived from actual tracked artifacts in the repository.

## 1. Ashburn Bare-Metal Native Benchmark
* **Exact Path:** `benchmarks/` and `core/` benchmark harnesses
* **Exact Command:** Documented in `benchmarks/BENCHMARKS.md` and script runners (`core/run_pipeline.sh`)
* **Execution Type:** Native C / Python integration
* **Workload Type:** Synthetic high-throughput event generation and stream processing
* **Queue Model:** Lock-free SPSC ring buffers, POSIX shared memory mapping (`shm_ipc.c`)
* **Validation:** Producer-consumer telemetry logs
* **Raw Evidence Path:** `benchmarks/results/scaling_matrix_raw.json`, `benchmarks/results/scaling_matrix_plot.csv`, `benchmarks/telemetry_snapshot/`
* **Limitations:** Requires dedicated multi-core NUMA architecture (tested on 128-core AMD EPYC host with PREEMPT_RT kernel). Not a live public mainnet financial gateway out of the box.
