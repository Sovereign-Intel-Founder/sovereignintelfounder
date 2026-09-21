# Sovereign Intelligence Protocol — Verification Runbook

This runbook provides the exact reproduction path, component mapping, and experimental boundaries for auditing the low-level systems primitives in this repository.

## 1. Quick Verification Path (Clone to Evidence)

```bash
git clone https://github.com/Sovereign-Intel-Founder/sovereignintelfounder.git
cd sovereignintelfounder

# Build and execute low-level lock-free SPSC ring buffer primitive
make lockfree_spsc_ring
./lockfree_spsc_ring

# Run the toll bridge concurrency test harness (256 workers)
python3 scripts/tollbridge_concurrency_test.py
```

## 2. Headline Metrics & Evidence Mapping

| Headline Metric | Measured Value | Source Path / Artifact | Exact Verification Command | Hardware & Execution Context |
|---|---|---|---|---|
| **Multi-Core Compute Saturation** | 2,787,589.29 ops/sec | `telemetry/` / `RAW_MATRIX.md` | `cat RAW_MATRIX.md` | 128-Core AMD EPYC, PREEMPT_RT Linux Kernel, core-pinned |
| **Ring Buffer Latency** | ~8.15 ns per op | `sip_core/` / `portfolio/` | `make lockfree_spsc_ring && ./lockfree_spsc_ring` | Bare-metal zero-copy POSIX shared memory mapping |
| **Network Concurrency Stress** | 1,121.84 req/sec | `tollbridge_system/` | `python3 scripts/tollbridge_concurrency_test.py` | 256 concurrent heavy multi-vector workers (100% success rate) |

## 3. Design Tradeoffs & Limitations
* **Synthetic Boundaries:** All stress telemetry and concurrency metrics reflect controlled synthetic workloads designed to isolate IPC and ring buffer bottlenecks. Live external network/wallet behaviors are intentionally excluded to keep benchmarks reproducible.
* **Hardware Requirements:** Peak multi-core saturation figures require NUMA-local node alignment and kernel thread priority configuration (`PREEMPT_RT`).
