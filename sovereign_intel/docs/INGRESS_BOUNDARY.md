# Ingress Boundary Specification

## Active Ingress Endpoint
* **URL:** `https://detective-standard-airplane-mountains.trycloudflare.com/v1/ingress`
* **Node:** `ashburn-baremetal`

## Current Processing Capabilities
1. **Reachability & TLS Termination:** Terminates secure connections at the Cloudflare edge proxy and proxies requests to the local bare-metal ingress daemon.
2. **Service Identification:** Returns cryptographically verifiable node identity metadata confirming protocol version (`SIP`) and deployment tier (`free`).
3. **Health & Status Interrogation:** Responds to standard status probes with structured JSON receipts.

## Excluded Capabilities (Current Phase)
* **Arbitrary Task Execution:** Does not currently accept unauthenticated remote task manifests over this public HTTP route.
* **Direct AF_XDP Ingestion:** Raw zero-copy packet rings operate at the kernel/driver layer on the bare-metal host and are isolated from direct public HTTP exposure.
* **Financial Execution:** Does not process or record live financial transactions or external trade execution via this public endpoint.
