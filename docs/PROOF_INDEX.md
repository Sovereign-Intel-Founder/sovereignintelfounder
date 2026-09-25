# Proof & Conformance Index

## 1. Protocol v1
* **Schemas:** Structured protocol definitions under repository schema paths.
* **Canonicalization:** Defined serialization rules for message interchange.
* **Valid Fixtures:** Standard conformance vectors representing valid protocol messages.
* **Adversarial Fixtures:** Malformed and boundary-test fixtures.
* **Expected Verification Behavior:** Deterministic rejection of malformed payloads and acceptance of canonical schemas.
* **Status:** verified

## 2. Kinetic Capsule Prototype
* **Exact Path:** `core/edge_arbitrage.py`, `core/max_arbitrage.py`
* **Architecture:** In-process arbitration and local pipeline modules.
* **What it proves:** Local decision logic and low-latency data flow under synthetic feeds.
* **What it does not prove:** Distributed consensus, multi-region low-latency execution, or live mainnet profitability.
* **Status:** tested prototype

## 3. Independent Conformance Verifier
* **Exact Path:** `core/validate_core_quota.py`, `core/validate_direct_gateway.py`
* **Fixture Scope:** Local validation scripts checking schema conformity and throughput bounds.
* **Independence Limitations:** Dependent on local test harness environment fixtures.
* **Status:** tested prototype

## 4. Rust Verifier
* **Exact Path:** Submodule / repository verifier components where present.
* **CLI:** Standard command-line interface for artifact checks.
* **Cryptographic & Semantic Checks:** Hash verification and structural validation.
* **Status:** partial / transport-only

## 5. Remote Handoff
* **Envelope Checks & Framing:** Message boundary and header verification.
* **Destination Checks & Expiration:** TTL and routing validation.
* **Replay Handling & Artifact Hash:** Nonce tracking and cryptographic fingerprinting.
* **Rust Semantic Verification:** Invoked where Rust verifier components are active.
* **Status:** transport-only

## 6. Limitations
* No live distributed consensus unless directly implemented.
* No remote execution claim unless directly implemented.
* No live memory migration claim.
* Generated fixtures are not live production evidence.
