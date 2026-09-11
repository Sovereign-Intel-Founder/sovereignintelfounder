# Sovereign Intelligence Protocol (SIP)

A high-performance event-routing and coordination layer designed for low-latency decentralized systems.

## Architecture
- **Ingress Layer**: High-throughput asynchronous entry points.
- **Toll Bridge**: Dynamic validation and rate-limiting gateway (`sip_core/bridge_mesh.py`).
- **Mesh Index**: Distributed node routing and state tracking (`sip_core/omni_mesh_engine.py`).
- **Latency Worker & Ledger**: Real-time telemetry, transaction processing, and execution logging (`sip_core/ledger_module.py`).

## Quick Start & Verification
Run the core verification harness in under 15 lines:
```bash
python3 examples/demo_runner.py

