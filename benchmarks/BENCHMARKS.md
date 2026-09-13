# High-Throughput Baseline Benchmarks

## System Architecture
* **Environment**: Bare-metal Linux (128 Cores, 728 GB RAM)
* **Target Workload**: Multi-chain mesh routing & ingestion engine

## 1. Process Scheduling & Context Switch Latency
Captured via `perf bench sched pipe`:
* **Total Operations**: 1,000,000 pipe operations
* **Execution Time**: 5.982 seconds
* **Latency per Operation**: **5.98 µs/op**
* **Throughput**: **167,146 ops/sec**

## 2. Ingestion Engine RPC Latency
Captured during 128-thread pipeline load testing (`omni_mesh_engine.py`):
| Metric / Route | Measured Latency | Frame Ingestion Status |
| :--- | :--- | :--- |
| Solana Live Endpoint | **1.069 ms - 1.329 ms** | Active Processing |
| Local RPC Transport | **0.011 ms** | Zero-Queue Drop |
| Base / Ethereum Pipeline | **0.202 ms - 0.325 ms** | Failover Handled |

