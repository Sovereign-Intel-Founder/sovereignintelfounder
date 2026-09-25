# Sovereign Intelligence Protocol (SIP)

A high-throughput, low-latency bare-metal protocol implementation featuring native telemetry harnesses, sharded memory queues, and modular verification layers. Optimized for high-frequency event streaming and hardware-aligned execution.

## Navigation & Documentation
* **[Start Here](docs/START_HERE.md):** Project overview, reading order, and scope.
* **[Repository Map](docs/REPOSITORY_MAP.md):** Structural layout of the codebase.
* **[Submodules](docs/SUBMODULES.md):** Explicit boundaries for auxiliary repositories (`clean-check`, `sovereign-intelligence`, `sovereign-seed-commons`).
* **[Benchmark Index](docs/BENCHMARK_INDEX.md):** High-throughput baseline metrics and evidence ledger.
* **[Proof Index](docs/PROOF_INDEX.md):** Verification assets, protocol fixtures, and status matrix.
* **[Demo Index](docs/DEMO_INDEX.md):** Safe local inspection and execution commands.
* **[Evidence Index](docs/EVIDENCE_INDEX.md):** Telemetry ledger and performance logs.
* **[Maturity & Limitations](docs/MATURITY_AND_LIMITATIONS.md):** Detailed breakdown of operational scope and boundaries.

## Maturity & Operational Scope
* **Project Stage:** Alpha / Founder-Engineered Prototype.
* **Operational Status:** Environment-dependent local synthetic harness. It is **not** a live financial execution gateway.
* **Evidence Categories:** Native C, Python, synthetic, captured, and server-only evidence are strictly categorized. Benchmark measurements reflect distinct operational scopes (e.g., producer-only enqueue vs. consumer-validated).
* **Architecture Boundaries:** Sovereign Intelligence Protocol (SIP) is strictly separate from **Sovereign Seed Commons**. The parent repository utilizes git submodules (`.gitmodules`) without code mixing or history rewriting.

## License
Distributed under the terms specified in the [LICENSE](LICENSE) file.
