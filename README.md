# Sovereign Intelligence Protocol (SIP) & Systems Portfolio

> **Active Colosseum Submission:** This directory (`coliseum-submission/`) preserves the Sovereign Intelligence Protocol entry currently under review. It is kept intact as submitted while the broader repository documents the engineering work and research behind SIP.

## About the Architect

I am **Joshua Kleinsasser**, a solo software developer, systems engineer, and founder of the **Sovereign Intelligence Protocol (SIP)**.

Over the past two years, I independently designed and developed SIP while investigating low-latency event routing, bridge and mesh architecture, concurrency, shared-memory communication, NUMA-aware execution, Linux performance, and telemetry on dedicated bare-metal infrastructure. The work was developed and benchmarked on a 128-core AMD EPYC system with 728 GB of RAM and documented through controlled experiments, raw measurements, failure analysis, and explicit methodology.

This repository presents selected evidence of that systems work. It combines the active Sovereign Intelligence Protocol competition entry with a modular, evidence-based C-primitives portfolio for engineers who value empirical results, reproducibility, and clearly stated limitations.

## Repository Layout
* `coliseum-submission/` - Active competition entry, architecture documentation, and benchmark claims (preserved for judging).
* `portfolio/` - Standalone low-latency C primitives, concurrency models, and hardware optimization research components.
* `EVIDENCE_INDEX.md` - Command, workload, output, and limitation index for verification.
* `PORTFOLIO_MAP.md` - Technical index mapping showcase files and their implementation status.
* `SECURITY.md` - Repository security, hygiene, and data handling standards.
