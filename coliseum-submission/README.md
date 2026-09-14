# Sovereign Intelligence Protocol

An ultra-low-latency market ingestion and processing pipeline engineered for high-frequency trading (HFT) and high-throughput systems. Developed and validated on high-end bare-metal infrastructure.

## Hardware & Environment Architecture
- **Processor**: 128-Core AMD EPYC (Ashburn)
- **Kernel**: Linux 6.x patched with `PREEMPT_RT` for deterministic microsecond-scale execution.
- **Networking**: Kernel bypass via `AF_XDP`, tuned NIC ring buffers, and 128 MB socket buffer allocations.
- **Topology**: NUMA-aware core pinning to eliminate cross-socket memory latency.

## Verified Performance Telemetry
- **Throughput**: Validated peak ingestion exceeding 345,788 Packets Per Second (PPS) with **0 dropped packets**.
- **Burst Handling**: Sustained processing of over 3.35 million events across heavy synthetic and live market PCAP replay workloads.

Refer to [BENCHMARKS.md](BENCHMARKS.md) for detailed telemetry logs, CPU power profiling, and system tuning parameters.
