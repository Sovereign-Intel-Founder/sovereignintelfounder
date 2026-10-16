# Flagship Pipeline Design Contract

## 1. System Overview
A single-producer, single-consumer (SPSC) bounded local ingestion pipeline providing explicit capacity limits, deterministic load-shedding (backpressure), failure isolation, and structured telemetry without network bloat or distributed consensus claims.

## 2. Core Specifications & Invariants
- **Queue Capacity:** Hard upper bound of 1,000 slots. Never exceeds configured maximum capacity.
- **Event Format:** UTF-8 encoded string records with strict schema validation. Malformed inputs are rejected immediately.
- **Concurrency Model:** 1 Producer thread, 1 Consumer thread. Relies on atomic head/tail indices with explicit memory ordering (`memory_order_acquire` / `memory_order_release`).
- **Full-Queue Behavior (Backpressure):** When capacity is exhausted, incoming events are explicitly rejected/dropped according to the configured drop policy. No blocking of producers unless specified by backpressure mode.
- **Accounting Invariant:** `Submitted = Accepted + Rejected + Failed`. No silent event loss.
- **Failure Isolation:** Upstream ingestion stalls or exceptions do not propagate to unrelated workers or cause process deadlock.
- **Memory Bound:** Heap and shared memory utilization remain bounded under sustained overload conditions.
- **Shutdown Semantics:** Graceful drainage or rejection of queued work without deadlocks across repeated start/stop cycles.
- **Telemetry Requirements:** Structured JSON output capturing exact commit hash, workload size, queue capacity, throughput, latency percentiles (p50, p95, p99), and rejection counts.
- **Security Boundary:** Local loopback (`127.0.0.1`) binding only; zero network-supplied command execution.

## 3. Scope Classification
- **Working Prototype:** Bounded SPSC queue, ingestion harness, and invariant test suite.
- **Out of Scope:** Multi-node consensus, hardware DPDK/AF_XDP network kernel bypass, live blockchain settlement, and enterprise-scale multi-cell routing.
