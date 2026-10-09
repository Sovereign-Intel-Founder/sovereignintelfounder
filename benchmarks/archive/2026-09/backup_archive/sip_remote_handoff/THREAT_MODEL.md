# SIP Remote Proof Handoff - Threat Model

| Threat Vector | Description & Mitigation Strategy |
|---|---|
| **Replay** | Attackers capture and resend valid transport envelopes. Mitigated by tracking `message_id` in a transient/persistent replay cache and enforcing strict `expires_at` checks. |
| **Interception** | Eavesdropping on loopback traffic. Mitigated in production via mTLS; prototype assumes secure local environment. |
| **Tampering** | Modifying envelope or artifact fields in transit. Mitigated by `artifact_sha256` hash binding and `transport_signature`. |
| **Wrong-Destination Delivery** | Misrouting messages between nodes. Mitigated by enforcing explicit `receiver_node_id` matching in the envelope. |
| **Sender / Receiver Impersonation** | Unauthorized entities acting as valid nodes. Mitigated by node identity binding and transport credentials. |
| **Oversized Payload DoS** | Flooding receiver with massive JSON payloads. Mitigated by strict byte-length limits on incoming streams before JSON parsing. |
| **Duplicate Delivery** | Simultaneous duplicate packet transmission. Mitigated by idempotent message ID checking. |
| **Stale Envelopes** | Transmitting old valid proofs long after validity window. Mitigated by `created_at` and `expires_at` sliding window validation. |
| **Compromised Transport Credentials** | Leakage of transport tokens. Mitigated by ephemeral session keys and strict separation from SIP artifact signing keys. |
| **Private-Key Exposure** | Risk of exposing SIP signing keys during handoff. Mitigated by design: private keys never leave the signing enclave/environment; only signed artifacts are transported. |
| **Verifier Substitution** | Replacing the Rust verifier with a weak validator. Mitigated by invoking the frozen, tested standalone `sip-verifier` binary. |
| **Confusion Between Transport Success and Proof Validity** | Assuming successful network delivery implies valid cryptographic proof. Mitigated by enforcing two-stage evaluation: successful transport wrapping $\rightarrow$ independent Rust verifier validation (`ACCEPTED`/`REJECTED`). |
