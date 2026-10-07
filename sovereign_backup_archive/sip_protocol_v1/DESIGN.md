# Sovereign Intelligence Protocol (SIP) — Protocol Specification v1

**Classification:** SIP PROTOCOL CONTRACT —IMMUTABLE SPECIFICATION (v1)

## 1. Overview
This specification freezes the data contract, signing rules, nine verification gates, and conformance fixture expectations for Sovereign Intelligence Protocol version 1 (`v1`). It establishes an interoperable boundary between task submitters, execution cells, and independent verifiers across any language implementation.

---

## 2. Protocol Names & Schema Identifiers
All v1 protocol objects must declare their exact type identity using these immutable identifiers:
- `sip.task_manifest.v1`
- `sip.capsule_checkpoint.v1`
- `sip.execution_receipt.v1`
- `sip.rejection.v1`

---

## 3. Signing Contract

### 3.1 Excluded Fields
The `signature` field itself is strictly excluded from the signed payload. An object must never sign a structure containing its own signature.

### 3.2 Signed Fields
All other required and optional fields defined within the schema for each respective object type are included in the signed payload.

### 3.3 Domain-Separation Prefixes
Each object type prepends a unique ASCII domain-separation prefix to the canonicalized bytes before hashing and signing:
- `sip.task_manifest.v1:`
- `sip.capsule_checkpoint.v1:`
- `sip.execution_receipt.v1:`
- `sip.rejection.v1:`

### 3.4 Canonicalization Method
*PROVISIONAL CANONICAL JSON — NOT YET RFC 8785 CONFORMANT*
The current prototype uses deterministic JSON serialization defined by Python's `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)` with UTF-8 encoding. Full RFC 8785 Canonical JSON implementation is designated for subsequent hardening releases.

### 3.5 Hash Algorithm
SHA-256 is used to hash the combined domain-separation prefix and canonical JSON bytes:
$$\text{payload\_hash} = \text{SHA256}(\text{domain\_prefix} \parallel \text{canonical\_json\_bytes})$$

### 3.6 Public-Key and Signature Encoding
- **Ed25519 Public Key:** Exactly 32 bytes, encoded in hexadecimal (64 hex characters) or raw bytes depending on container context.
- **Ed25519 Signature:** Exactly 64 bytes, encoded in hexadecimal (128 hex characters) or raw bytes.

### 3.7 Sequence Numbers and Nonces
- **`sequence_number`:** A monotonically increasing non-negative 64-bit integer (`uint64`) tracking the exact step progression within a capsule lineage.
- **`nonce`:** A cryptographically secure random string or UUID generated per transition to guarantee single-use freshness and prevent replay attacks.

### 3.8 Timestamp Format
Timestamps are strictly encoded as UTC strings in extended ISO 8601 format with explicit millisecond precision and UTC timezone indicator (e.g., `2026-09-24T02:00:00.000Z`). Timestamps serve as signed metadata and temporal policy boundaries.

### 3.9 Error Format
Rejection payloads utilize structured JSON objects containing machine-readable error codes and descriptive human-readable strings.

---

## 4. The Nine Verification Gates

| Gate ID | Gate Name | Input Fields | Rejection Code | Timing | Deterministic? |
|---|---|---|---|---|---|
| 1 | Schema & Version Validity | `schema`, structural types | `schema_invalid` | Before Signature | Yes |
| 2 | Canonical Serialization | Raw payload bytes | `canonicalization_invalid` | Before Signature | Yes |
| 3 | Identity Validity | `capsule_id`, `task_id` | `identity_mismatch` | Before Signature | Yes |
| 4 | Signature Validity | `signature`, `public_key` | `signature_invalid` | Signature Check | Yes |
| 5 | Commitment Integrity | `state_hash`, `input_hash` | `commitment_mismatch` | After Signature | Yes |
| 6 | Destination Authorization | `destination_cell_id` | `destination_unauthorized` | After Signature | Yes |
| 7 | Nonce & Sequence Freshness | `nonce`, `sequence_number` | `nonce_reused` / `sequence_invalid` | After Signature | Yes |
| 8 | Lineage & State Transition | `prev_receipt_hash`, `state` | `lineage_invalid` / `state_transition_invalid` | After Signature | Yes |
| 9 | Expiration & Policy | `expires_at`, revocation lists | `capsule_expired` / `resource_policy_denied` | After Signature | Yes |
