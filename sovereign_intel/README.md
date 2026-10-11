# Sovereign Intelligence Protocol (SIP)

Institutional-grade, cryptographically verifiable low-latency execution and event ingestion architecture.

## Canonical Node Infrastructure
* **Active Node:** `ashburn-baremetal` (128-core AMD EPYC, 728GB RAM, Ashburn, VA)
* **Canonical Ingress Endpoint:** `https://detective-standard-airplane-mountains.trycloudflare.com/v1/ingress`
* **Live Status Documentation:** [docs/LIVE_NODE_STATUS.md](docs/LIVE_NODE_STATUS.md)
* **Ingress Boundary Specification:** [docs/INGRESS_BOUNDARY.md](docs/INGRESS_BOUNDARY.md)
* **Cryptographic Attestation:** [evidence/node_attestation.json](evidence/node_attestation.json)

---

## Component Status Matrix

| Component | Operational Status | Verification Source |
|---|---|---|
| Native driver attachment | Measured & Verified | Server-resident hardware telemetry |
| AF_XDP socket initialization | Measured & Verified | Low-level kernel bindings |
| UMEM zero-copy mapping | Measured & Verified | Memory allocation proofs |
| Hardware frame redirection | Verified with raw evidence | Benchmark harness logs |
| Active polling consumer ring | Active / Hardening | Local test runners |
| Application-level ingress | Documented | [docs/INGRESS_BOUNDARY.md](docs/INGRESS_BOUNDARY.md) |
| Live endpoint (`/v1/ingress`) | Active & Reachable | Public Cloudflare Tunnel proxy |
| Financial execution / Live trading | Not Established | Explicitly out of current endpoint scope |

---

## Cryptographic Guarantees & Verification
All active nodes are bound to specific Git revisions using Ed25519 cryptographic signatures. 
* **Key ID:** `sip-ed25519-ashburn-01`
* **Current Commit Binding:** `d002eb2`

To verify node attestation locally:
```bash
python3 src/sovereign/core/crypto/ed25519_verify.py evidence/node_attestation.json
