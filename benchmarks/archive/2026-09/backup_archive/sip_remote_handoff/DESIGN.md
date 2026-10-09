# SIP Remote Proof Handoff - Architectural Design

## 1. Sender Behavior
* Selects an existing valid SIP v1 artifact (task manifest, checkpoint, or receipt).
* Wraps the artifact in a standardized JSON transport envelope.
* Transmits the envelope to a designated receiver endpoint over local loopback.
* **Strict Constraint**: Never transmits private signing keys or shared secret material.

## 2. Receiver Behavior
* Authenticates the transport peer session.
* Validates incoming envelope payload size and JSON structural format.
* Checks `message_id` against active replay cache state.
* Extracts the inner SIP artifact.
* Invokes the standalone Rust verifier binary/library (`sip-verifier`) against the extracted artifact.
* Returns `ACCEPTED` or `REJECTED` with a structured reason code.
* **Strict Constraint**: Never executes or interprets the payload as an executable workload.

## 3. Transport Envelope Fields
* `envelope_version`: Protocol version specifier (e.g., `"sip-transport-v1"`).
* `message_id`: Unique message identifier (UUIDv4 or nonce).
* `sender_node_id`: Identifier of the sending node.
* `receiver_node_id`: Expected identifier of the receiving node.
* `artifact_type`: Classification (`task_manifest`, `checkpoint`, `receipt`).
* `artifact_sha256`: Cryptographic hash binding of the inner artifact.
* `artifact`: The raw JSON object representing the SIP artifact.
* `created_at`: UTC timestamp of envelope creation.
* `expires_at`: UTC expiration timestamp.
* `transport_signature`: Cryptographic signature over the transport envelope metadata (distinct from the inner SIP artifact signature).

## 4. Separation of Concerns
1. **Transport Authentication**: Validates message transport integrity and peer identity.
2. **Artifact Signature Verification**: Validates inner SIP Ed25519 cryptographic signatures using domain separation labels.
3. **Artifact Semantic Verification**: Enforces protocol rules (lineage, sequence continuity, expiration).
4. **Replay Protection**: Prevents duplicate processing of previously observed `message_id`s or replayed checkpoints.
5. **Authorization Policy**: Determines whether an authenticated peer is permitted to submit artifacts to the receiver.

## 5. Failure Behavior & Error Handling
* **Malformed Envelope**: Reject immediately with `MALFORMED_ENVELOPE`.
* **Oversized Message**: Reject immediately with `PAYLOAD_TOO_LARGE`.
* **Wrong Receiver**: Reject immediately with `INVALID_DESTINATION`.
* **Expired Envelope**: Reject immediately with `ENVELOPE_EXPIRED`.
* **Duplicate Message ID**: Reject immediately with `REPLAY_DETECTED`.
* **Artifact Hash Mismatch**: Reject immediately with `HASH_MISMATCH`.
* **Invalid Artifact Signature**: Reject via Rust verifier with `INVALID_SIGNATURE`.
* **Valid Signature but Invalid Semantics**: Reject via Rust verifier with protocol rejection reason (e.g., lineage break).
* **Unsupported Envelope Version**: Reject immediately with `UNSUPPORTED_VERSION`.
