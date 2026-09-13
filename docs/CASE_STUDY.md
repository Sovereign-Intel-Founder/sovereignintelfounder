# Bare-Metal High-Concurrency Infrastructure: Case Study

## Executive Summary
Engineered and benchmarked a high-throughput, asynchronous mesh routing engine on bare-metal dual-socket Linux hardware (128 cores, 728 GB RAM) located in Ashburn, VA.

## Key Technical Achievements
1. **NUMA Interconnect Optimization**: Identified and documented a **35.31% throughput penalty** during unpinned cross-socket memory reads. Enforced thread locality via `numactl` to eliminate cross-node memory latency.
2. **Full System Saturation**: Pushed aggregate memory bus bandwidth to **72.27 GB/sec (68,919.20 MiB/sec)** across 128 parallel worker threads with an average latency of **1.40 ms**.
3. **Kernel & Scheduler Latency**: Achieved **166,901 ops/sec** (~5.99 µs per operation) pipe context-switching throughput under tuned kernel CPU governor settings (`performance`).
4. **Continuous Regression Control**: Automated latency validation via `scripts/ci_bench.sh` to prevent performance regressions in CI/CD pipelines.
