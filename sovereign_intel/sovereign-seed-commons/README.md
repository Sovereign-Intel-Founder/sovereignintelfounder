# Sovereign Seed Commons

Participant-layer architecture and cell execution framework for the Sovereign Intelligence Protocol (SIP).

## Overview
The Sovereign Seed Commons provides the distributed participant layer, cryptographic lineage verification, and cell execution environment that interfaces with the core SIP infrastructure.

## Architecture & Components
* **Cell Runners:** Secure execution environments for decentralized telemetry and state transitions.
* **Evidence Validators:** Cryptographic scripts enforcing SHA-256 lineage verification and state integrity.
* **Relationship to SIP:** Operates as the decentralized participant tier feeding verifiable data payloads into the core bare-metal ingestion engine (`ashburn-baremetal`).

## Quickstart & Validation
To run the local evidence validator and verify repository cell integrity:
```bash
python3 tools/cell_runner.py --validate
```

## Governance & License
Licensed under the Apache 2.0 open-source license. See the [LICENSE](LICENSE) file for details.
