# ⚡ Sovereign Intelligence Systems Laboratory
### Verified Bare-Metal Benchmark & Performance Audit Showcase

Welcome to the official performance verification registry for Sovereign Intelligence infrastructure workloads. All test suites are executed in a deterministic, read-only testing harness on our dedicated 128-core AMD EPYC bare-metal host (728GB RAM).

---

## 📊 Featured Audit: Component Performance Matrix (Ref: GQI-EA-202610)

| Index ID | Evaluated Functional Boundary | Workload Scope / Source Target | Status |
| :--- | :--- | :--- | :--- |
| **Component 1** | Core Execution Interface | 48 test variations (1–8 worker scaling) | **Validated** |
| **Component 2** | Payload Processing Pipeline | 48 test variations (1–8 worker scaling) | **Validated** |
| **Component 3** | Checksum & Validation Engine | 48 test variations (1–8 worker scaling) | **Validated** |
| **Component 4** | Metadata & Header Generator | 48 test variations (1–8 worker scaling) | **Validated** |
| **Component 5** | Temporal Indexing & Timestamp Handler | 48 test variations (1–8 worker scaling) | **Validated** |
| **Component 6** | Command Dispatch & Routing Interface | 48 test variations (1–8 worker scaling) | **Validated** |
| **Component 7** | Secondary API Inquiry Subsystem | Incomplete implementation stub (`pass` / returns `None`) | **Excluded (PLACEHOLDER_INCOMPLETE)** |
| **Component 8** | Diagnostic Log Retrieval Subsystem | Missing state target (`GQI-EA/data/logs/` directory) | **Excluded (BLOCKED_MISSING_STATE)** |

### 📥 Download Verified Artifacts
* **[View Executive PDF Report](./benchmarks/active-showcase/gqi_ea_benchmark_report.pdf)** (Complete hardware context, numbered component mapping, latency percentiles $p_{50}, p_{95}, p_{99}$, and throughput metrics).
* **[Download Raw Evidence Archive (.tar.gz)](./benchmarks/active-showcase/gqi_ea_benchmark_evidence_with_negative_paths_20261017T183000Z.tar.gz)** (Includes 384 raw JSON/CSV records, environment specs, test assertions, and SHA-256 cryptographic manifests).

---
*(All benchmarks executed under strict read-only parameters with zero source modification).*

---
