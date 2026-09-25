# Proof & Conformance Index

## Verification & Architecture Assets
* **Protocol Schemas & Manifests:** Structured definitions under repository paths.
* **Kinetic Capsule Prototypes:** Local arbitration and low-latency pipeline modules (`core/edge_arbitrage.py`, `core/max_arbitrage.py`).
* **Independent Conformance Verifier:** Local verification scripts (`core/validate_core_quota.py`, `core/validate_direct_gateway.py`).
* **Rust Verifier:** Memory-safe verification modules where present.
* **Remote Handoff:** Architecture designed for decoupled multi-cell scale-out.

## Maturity & Verification Matrix
* **Verified (Local Synthetic Harness):** Throughput metrics exceeding 133,000 events/sec peak, lock-free SPSC queue performance.
* **Prototype (Local Environment):** Multi-affinity binding, sharded memory queues, local SQLite persistence (`core/data/toll_ledger.db`).
* **Planned / Environment-Dependent:** On-chain integration, multi-cell (27-cell) distributed mesh expansion.
