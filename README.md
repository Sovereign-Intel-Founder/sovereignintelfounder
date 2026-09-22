# Sovereign Intelligence Protocol (SIP)

A high-performance local simulation and research prototype focused on low-latency concurrency, secure IPC, and automated CI security guardrails.

---

## Overview

The Sovereign Intelligence Protocol (SIP) is a systems-engineering project built to explore low-latency data ingestion, lock-free concurrency, and rigorous security practices in Python and C. 

> **Note:** This repository is a **local simulation and research prototype** built for performance experimentation and security architecture design.

---

## Key Features & Architecture

* **Core Pipeline:** Python-based stream ingestion and modular event processing handlers.
* **Low-Latency Components:** Custom C single-producer single-consumer (SPSC) lock-free ring buffer (`portfolio/src/lockfree_spsc_ring.c`) optimized with `-O3` flags.
* **Secure Networking:** All core network bindings default strictly to loopback (`127.0.0.1`) and can be configured safely via the `SIP_BIND_HOST` environment variable.
* **Automated CI Security Guardrails:** Custom GitHub Actions workflows configured to aggressively scan for and block unauthorized `shell=True` usages and wildcard network bindings (`0.0.0.0`) in core network paths.

---

## Security & Hardening History

As part of ongoing architectural audits, this repository underwent a rigorous security sweep:
* Permanently removed unauthenticated remote command execution (RCE) bridge modules.
* Hardened network bindings to eliminate wildcard listeners by default.
* Established automated repository-level CI security guardrails to enforce continuous compliance.

---

## Getting Started

### Prerequisites
* Python 3.10+
* GCC (with C11 support)
* Make

### Quickstart & Verification

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Sovereign-Intel-Founder/sovereignintelfounder.git](https://github.com/Sovereign-Intel-Founder/sovereignintelfounder.git)
   cd sovereign-intelligence
