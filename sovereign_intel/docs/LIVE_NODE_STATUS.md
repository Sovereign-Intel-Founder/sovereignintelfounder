# Live Node Status & Operational Specification

## Canonical Endpoint Metadata
* **Canonical Ingress URL:** `https://detective-standard-airplane-mountains.trycloudflare.com/v1/ingress`
* **Node Identifier:** `ashburn-baremetal`
* **Protocol Version:** `SIP`
* **Service Tier:** `free` (Public Testnet / Demonstration Ingress)
* **Infrastructure Type:** Cloudflare Tunnel backing dedicated 128-core AMD EPYC bare-metal server (728GB RAM, Ashburn, VA)
* **Last Status Check:** 2026-10-11

## Endpoint Response Schema
```json
{
  "status": "success",
  "protocol": "SIP",
  "node": "ashburn-baremetal",
  "tier": "free"
}
```

## Operational Scope & Guarantees
* **Purpose:** Demonstrates live endpoint reachability, TLS termination, protocol identification, and service identity.
* **What it Proves:** The edge proxy and ingress daemon are active on the designated bare-metal hardware.
* **What it Does Not Prove:** It does not independently prove application-level task execution, AF_XDP zero-copy packet ingestion, or cryptographic receipt generation without companion signed attestations.
