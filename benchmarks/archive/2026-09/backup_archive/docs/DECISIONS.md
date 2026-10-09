# Architecture Decision Records (ADR)

## 1. Choice of SPSC Ring Buffer Over MPMC
* **Decision:** Implement a Single-Producer Single-Consumer (SPSC) lock-free ring buffer for core IPC rather than a Multi-Producer Multi-Consumer (MPMC) queue.
* **Rationale:** In high-throughput event routing pipelines, MPMC queues introduce heavy cache-line bouncing and expensive Compare-And-Swap (CAS) contention under high thread concurrency. SPSC guarantees atomic head/tail progression without atomic retry loops, keeping latency deterministic at the nanosecond scale.

## 2. Memory Ordering Semantics (`acquire`/`release`)
* **Decision:** Utilize explicit acquire-release semantics (`memory_order_acquire` / `memory_order_release`) rather than sequential consistency (`memory_order_seq_cst`) or volatile locks.
* **Rationale:** Sequential consistency imposes unnecessary memory barrier overhead across CPU pipelines. Acquire-release synchronization ensures precise ordering constraints between producer writes and consumer reads while allowing optimal CPU out-of-order execution headroom.

## 3. NUMA Locality and Core Pinning
* **Decision:** Enforce strict CPU core pinning and NUMA-local memory allocation for low-latency workers.
* **Rationale:** Cross-socket memory access over interconnect buses introduces variable non-deterministic latency spikes. Pinning threads to local cores on the 128-core AMD EPYC host isolates execution contexts and minimizes cache misses.

## 4. Synthetic Benchmarking Boundaries
* **Decision:** Rely on controlled synthetic workloads to measure IPC, ring buffer throughput, and concurrency scaling.
* **Rationale:** Live external network feeds and wallet broadcast behaviors introduce uncontrollable network jitter and external rate limits. Synthetic workloads isolate the internal component boundaries, ensuring reproducible, verifiable telemetry.
