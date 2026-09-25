# Sovereign Intelligence Protocol (SIP)

A high-throughput, low-latency bare-metal protocol implementation featuring native telemetry harnesses, sharded memory queues, and modular verification layers. Optimized for high-frequency event streaming and hardware-aligned execution.

## Navigation & Documentation
* **[Start Here](docs/START_HERE.md):** Project overview, reading order, and scope.
* **[Repository Map](docs/REPOSITORY_MAP.md):** Structural layout of the codebase.
* **[Benchmark Index](docs/BENCHMARK_INDEX.md):** High-throughput baseline metrics (exceeding 133,000 events/sec peak on 128-core Ashburn bare-metal).
* **[Proof Index](docs/PROOF_INDEX.md):** Verification assets and protocol fixtures.
* **[Demo Index](docs/DEMO_INDEX.md):** Safe local inspection and execution commands.
* **[Evidence Index](docs/EVIDENCE_INDEX.md):** Telemetry ledger and performance logs.
* **[Submodules](docs/SUBMODULES.md):** Explicit boundaries for auxiliary repositories (`clean-check`, `sovereign-intelligence`, `sovereign-seed-commons`).
* **[Security & Hygiene](docs/SECURITY_AND_DATA_HYGIENE.md):** Containment policies and quarantine rules.

## Maturity & Limitations
* **Project Stage:** Alpha / Founder-Engineered Prototype.
* **Hardware Dependencies:** Certain core affinity and ring-buffer modules require dedicated multi-core NUMA architectures.
* **Boundaries:** Sovereign Seed Commons is maintained as a strictly separate project and is not merged into SIP.

## License
Distributed under the terms specified in the [LICENSE](LICENSE) file.
