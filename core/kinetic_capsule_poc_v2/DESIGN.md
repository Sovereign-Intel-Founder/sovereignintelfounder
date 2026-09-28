# Design Specification — Process-Boundary Prototype (v2)

## Identity & Commitments
- **Capsule Identity:** Unique UUID (`capsule_id`), tied to `task_id`.
- **Code & Input Commitments:** SHA-256 hashes of task code and input parameters.
- **Canonical JSON:** All signed structures are serialized via sorted keys without white space before hashing.

## Cryptography & Lineage
- **Ed25519 Signatures:** Keypairs generated at runtime via PyNaCl.
- **Receipt Lineage:** Each execution step appends a receipt containing the previous receipt hash, creating an append-only chain.

## Security & Verification
- **Cell Authorization:** Destination cells verify cell IDs against authorization lists.
- **Nonce & Sequence:** Monotonically increasing sequence numbers and single-use nonces prevent replay attacks.
- **State Recomputation:** Verifiers recompute the entire state transition off-line to validate computation correctness.
