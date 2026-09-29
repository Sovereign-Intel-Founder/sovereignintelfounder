# Sovereign Intelligence Protocol — v0.1.0 Reproducible Baseline

## Proven Scope & Verified Mechanics
* **Fresh Linux Build & Compilation**: Clean checkout verification via `make clean && make all`.
* **C-Level Memory Safety**: Fully passing AddressSanitizer (ASan) and UndefinedBehaviorSanitizer (UBSan) runs (`make sanitize`) on lock-free SPSC ring buffer implementations (`spsc_ring.c`).
* **Python Application Test Suites**: 100% pass rate across `arbitrage` (4/4) and `sip_depot` (7/7) unit testing suites.
* **Local Synthetic Concurrency**: Verified backpressure recovery, queue saturation handling, and upstream failure isolation under local synthetic test harnesses.

## Scope Boundaries & Unverified Items
* **No Mainnet Settlement**: Protocol has not been deployed to or tested against live mainnet state or RPC settlement layers.
* **No Live Trading Execution**: Execution logic is validated exclusively against mock simulators and isolated ring buffers; no real capital or live market order routing has been executed.
* **No Independent Performance Certification**: Latency numbers and throughput metrics represent local bare-metal benchmarks and have not been certified by an independent third-party auditor.
