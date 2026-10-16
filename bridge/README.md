# Sovereign Bridge

## Status
* **Status:** Operational[cite: 3]
* **Purpose:** High-throughput event ingestion, toll bridge data routing, and low-latency Solana-adjacent data pipelines.

## Entry Point
* Start daemon: `python3 operations/toll_bridge_daemon.py`

## Dependencies & Hardware
* **Services:** Uvicorn, SQLite ledger, local test validator.
* **Ports:** 8003 (Ingress), 9872 (Daemon Worker), 8000 (Validator).

## Security Boundary
* Restricted to authenticated mesh endpoints and internal loopback/IPC handlers.

## Evidence & Testing
* Validated via synthetic workload benchmark suites located in `benchmarks/` and telemetry logs in `evidence/`.
