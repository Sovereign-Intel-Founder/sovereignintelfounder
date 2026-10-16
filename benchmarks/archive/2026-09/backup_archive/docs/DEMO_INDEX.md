# Sovereign Intelligence Protocol (SIP) Demo Index

| Demonstration Name | Path | Exact Command | Input Type | Scope / Execution | CI Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rust Verifier Conformance** | `sip-verifier/` | `cargo run --manifest-path sip-verifier/Cargo.toml -- --fixtures sip_protocol_v1/fixtures --conformance` | Static JSON Fixtures | End-to-end cryptographic & schema validation | Yes |
| **Kinetic Capsule v2** | `kinetic_capsule_poc_v2/` | `python3 -m kinetic_capsule_poc_v2.demo_controller` | Synthetic State | Inter-process checkpoint handoff | Yes |
| **Remote Handoff Receiver** | `sip-remote-handoff/` | `python3 sip-remote-handoff/receiver.py` | Network Frame / Stdin | Loopback-scoped transport verification | Yes |
| **Toll Bridge SPSC Benchmarks** | `tollbridge_system/` | `make demo` | Synthetic Workload | Native ring-buffer telemetry | Yes |
| **Python Flagship Model** | `sip_depot/` | `python3 sip_depot/flagship_harness.py --matrix` | Generated Matrix | Application-layer model simulation | Yes |
