# Bare-Metal High-Performance System Benchmarks

## 1. Single-Threaded Latency & Bandwidth Baseline
* **Local NUMA Memory Bandwidth (Node 0)**: $20.84\text{ GB/sec}$
* **Cross-Node NUMA Memory Bandwidth (Node 0 CPU -> Node 1 RAM)**: $13.48\text{ GB/sec}$
* **Measured Cross-Socket Interconnect Penalty**: $35.31\%$ degradation

$$\text{Interconnect Penalty} = \left(1 - \frac{13.48\text{ GB/s}}{20.84\text{ GB/s}}\right) \times 100 = 35.31\%$$

* **Single-Thread Context-Switch Throughput**: $166,901\text{ ops/sec}$
* **Single-Thread Context-Switch Latency**: $\approx 5.99\ \mu\text{s/op}$

$$\text{Latency} = \frac{1}{166,901\text{ ops/sec}} \approx 5.991\ \mu\text{s}$$

## 2. 128-Core Multi-Socket Saturation Performance
* **Total Parallel Memory Throughput**: $68,919.20\text{ MiB/sec}$ ($\mathbf{72.27\text{ GB/sec}}$)
* **Execution Block Size**: $102,400\text{ MiB}$ transferred across 128 active worker threads
* **Average Parallel Latency**: $1.40\text{ ms}$ ($0.03\text{ ms}$ min, $1.61\text{ ms}$ 95th percentile)
* **Total Benchmark Execution Time**: $1.4854\text{ seconds}$

$$\text{Aggregate Throughput} = \frac{102,400\text{ MiB}}{1.4854\text{ s}} = 68,937.66\text{ MiB/s} \approx 72.27\text{ GB/s}$$

## 3. Low-Latency Kernel Tuning & Environment Setup
* **Host Location**: Ashburn, VA Bare-Metal Node
* **Topology**: Dual-Socket 128-Core CPU / 728 GB RAM
* **CPU Frequency Governor**: `performance` locked across all 128 physical cores
* **Power Management**: C-state deep sleep disabled to prevent microsecond wake-up jitter
