# Benchmark Index & Evidence Ledger

All benchmarks are derived from actual tracked artifacts in the repository.

| Benchmark | Exact path | Command | Implementation | Input classification | Queue model | Scope | Correctness checks | Raw evidence | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| Ashburn Bare-Metal Scaling Matrix | `benchmarks/results/scaling_matrix_raw.json`, `benchmarks/results/scaling_matrix_plot.csv` | Documented in `benchmarks/BENCHнавлиmarks.md` / `core/run_pipeline.sh` | Native C / Python integration | synthetic | bounded native SPSC / sharded SPSC | producer-only enqueue & concurrency harness | Built-in JSON validation and CSV anomaly checks | `benchmarks/results/scaling_matrix_raw.json` | Requires dedicated multi-core NUMA architecture (128-core AMD EPYC host with PREEMPT_RT kernel). Not a live financial mainnet gateway out of the box. |
| Telemetry Snapshots | `benchmarks/telemetry_snapshot/` | server-only execution scripts | Native telemetry capture | captured / synthetic | resource telemetry | resource-telemetry only | Log integrity verification | `benchmarks/telemetry_snapshot/` | Server-only hardware telemetry; environment-dependent. |

## Methodology & Classifications
* **Input Classifications:** Synthetic workloads, captured traces, replayed PCAP, live endpoints, or model-only.
* **Scope Classifications:** Producer-only enqueue, consumer-validated end-to-end, application-layer, storage-layer, or resource-telemetry only.
