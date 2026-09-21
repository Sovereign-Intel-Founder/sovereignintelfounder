# Sovereign Intelligence Protocol — Verification Runbook

This runbook provides the exact reproduction path, component mapping, and experimental boundaries for auditing the low-level systems primitives in this repository.

## 1. Local Verification Path (Reproducible from Clone)

The following components can be built and executed on any standard Linux development environment:

```bash
git clone https://github.com/Sovereign-Intel-Founder/sovereignintelfounder.git
cd sovereignintelfounder

# Build and execute lock-free SPSC ring buffer primitive
make lockfree_spsc_ring
./lockfree_spsc_ring

# Run the toll bridge concurrency test harness (256 workers)
python3 scripts/tollbridge_concurrency_test.py
```

## 2. Headline Metrics & Telemetry Provenance

To maintain absolute transparency, metrics are categorized by execution boundary:

| Headline Metric | Reported Value | Provenance / Classification | Source Artifact | Execution Context |
|---|---|---|---|---|
| **Multi-Core Compute Saturation** | 2,787,589.29 ops/sec | **Ashburn Bare-Metal Telemetry** (Archived Measurement) | `RAW_MATRIX.md` / `telemetry/` | 128-Core AMD EPYC, PREEMPT_RT Kernel, core-pinned |
| **Ring Buffer Latency** | ~8.15 ns per op | **Hardware-Validated Measurement** (Source-level probe) | `sip_core/` / `portfolio/` | Zero-copy POSIX shared memory mapping |
| **Network Concurrency Stress** | 1,121.84 req/sec | **Locally Reproducible Test** | `scripts/tollbridge_concurrency_test.py` | 256 concurrent multi-vector workers (100% success rate) |

## 3. Design Tradeoffs & Limitations
* **Hardware Dependence:** Peak multi-core saturation and nanosecond ring buffer bounds require dedicated NUMA-local node alignment and kernel thread priority configuration (`PREEMPT_RT`). Standard consumer hardware will yield different baseline deltas.
* **Synthetic Boundaries:** All stress telemetry reflects controlled synthetic workloads designed to isolate IPC and ring buffer bottlenecks. Live external network/wallet behaviors are intentionally excluded.
