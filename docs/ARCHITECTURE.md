# High-Concurrency Engine Architecture & NUMA Layout

## 1. Top-Level Architectural Overview
The engine uses an asynchronous, multi-threaded routing mesh engineered for bare-metal multi-socket Linux hardware.

## 2. Hardware Topology & Thread Binding
* **Core Count**: 128 physical cores across 2 NUMA domains.
* **Memory Routing**: Worker threads are pinned to local NUMA nodes (`numactl --cpunodebind`) to avoid cross-socket interconnect latencies.
* **Measured Memory Overhead**: Unpinned cross-node reads introduce a **35.3% throughput penalty** (20.84 GB/s local vs 13.48 GB/s cross-node).

## 3. Fault Tolerance & Zero-Lock Isolation
* **Socket Failures**: Transport drops on bridge gateways are handled asynchronously without blocking core processing threads.
* **Lifecycle Guarantees**: Clean event loop teardown catching `CancelledError` without orphaned background processes.
