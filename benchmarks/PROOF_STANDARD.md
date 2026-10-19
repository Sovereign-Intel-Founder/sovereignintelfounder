# Sovereign Intelligence Protocol — Proof & Evidence Standard

## Core Principles
1. **Separation of Source and Evidence**: Source code, build instructions, and raw execution outputs must never be intermixed.
2. **Immutable Result Isolation**: Every run must be stored under its unique benchmark ID and dated run ID (`results/<benchmark-id>/<run-id>/`).
3. **Mandatory Checksums**: All stored results must include cryptographic SHA-256 checksums (`sha256sums.txt`).
