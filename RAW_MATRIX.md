# Raw Benchmark Telemetry Matrix

| Metric Category | Target Component | Measured Value | Hardware / Execution Context |
|---|---|---|---|
| Multi-Core Compute Saturation | `sip_core` SPSC Pipeline | 2,787,589.29 ops/sec | 128-Core AMD EPYC, PREEMPT_RT Kernel |
| Ring Buffer Latency | SPSC Ring Buffer | ~8.15 ns per operation | Bare-metal zero-copy memory mapping |
| Network Concurrency Stress | Tollbridge Gateway | 1,121.84 req/sec (100% success) | 25,000 heavy multi-vector payloads (265 workers) |
| Tail Latency (p50 / p99) | IPC Routing Pipeline | 94.88 ms / 318.56 ms | 128 concurrent workers / 5,000 probes |
