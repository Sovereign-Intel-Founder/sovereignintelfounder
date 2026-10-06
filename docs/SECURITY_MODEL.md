# Security Model

The project already contains a substantial layered security model. The cleanup is consolidating, documenting, and removing legacy ambiguity—not building security from scratch.

## Core Mechanisms & Source Paths
- **HMAC/Authentication & Ingress**: Verified in core routing and ingest modules (`sip_remote_handoff/`, ingestion pipelines).
- **Ed25519 Canonical Envelopes & Handoff**: Constant-time signature comparison and envelope validation in `sip_remote_handoff` sender/receiver suites.
- **Nonce, Replay Protection & Freshness**: Timestamp validation and nonce tracking routines.
- **Durable Idempotency & SQLite WAL Persistence**: High-concurrency state tracking via SQLite Write-Ahead Logging.
- **Evidence & Lineage Validation**: Cryptographic proof returns and lineage check functions.

## Legacy / Test-Only Paths
- Older simulation, mock, and demo harness files are explicitly categorized as legacy or test-only.

## Limitations
- Relies on secure key storage on host environments; public binary artifacts are excluded from repository tracking.
