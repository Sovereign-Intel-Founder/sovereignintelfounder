# Sovereign Intelligence Protocol (SIP) - Final Advanced Benchmark Report
**Date:** September 23, 2026  
**Repository:** https://github.com/Sovereign-Intel-Founder/sovereignintelfounder  
**Commit Hash:** 3d373f7334d1818a759b1698831a99cae567ec6d  

---

## 1. Scope and Repository Identity
This document records the finalized benchmark suite and resource telemetry for the Sovereign Intelligence Protocol (SIP) software architecture, executed on a dedicated bare-metal server environment (128-core AMD EPYC, 728 GB RAM, dual 10GbE SFP+, Linux PREEMPT_RT kernel).

## 2. Benchmark Classifications
The results in this report adhere strictly to the following designations:
* MEASURED CURRENTLY
* SYNTHETIC INPUT
* LOCAL EXECUTION
* PRODUCER-ONLY
* CONSUMER-VALIDATED
* RESOURCE-INSTRUMENTED
* HISTORICALLY RECORDED
* CAUSE NOT PROVEN
* NOT AN END-TO-END RESULT

## 3. Python/SQLite/WAL Concurrency Result
* **Classification:** MEASURED CURRENTLY, SYNTHETIC INPUT, LOCAL EXECUTION
* **Metrics:** 12,800,000 events processed; approximately 393,616 events/sec in full-scale run; zero rejected events.
* **Storage:** SQLite `journal_mode` verified as WAL.

## 4. Native Producer-Only Enqueue Result
* **Classification:** PRODUCER-ONLY, SYNTHETIC INPUT, LOCAL EXECUTION, NOT AN END-TO-END RESULT
* **Metrics:** Approximately 21,123,222 events/sec global wall-clock rate (12,800,000 submitted / successful enqueue returns).
* **Important Note:** This harness uses 128 producers on one shared ring; it is **not an SPSC result**, **not end-to-end**, and **not zero-contention**.

## 5. Native Bounded SPSC Wraparound and Consumer-Completion Result
* **Classification:** CONSUMER-VALIDATED, SYNTHETIC INPUT, LOCAL EXECUTION
* **Metrics:** 4,096-entry ring; 12,800,000 events enqueued, dequeued, validated, and completed; approximately 1,783,182.96 completed events/sec; 3,124 wraparound cycles.
* **Integrity:** Zero errors, drops, duplicates, missing events, out-of-order deliveries, or checksum mismatches.

## 6. Native Bounded SPSC Backpressure and Recovery Result
* **Classification:** CONSUMER-VALIDATED, RESOURCE-INSTRUMENTED, LOCAL EXECUTION
* **Metrics:** 4,096-entry ring; 1,000,000 events completed; approximately 1,532,296.95 completed events/sec; 8,594 queue-full and retry/spin observations; maximum queue depth reached 4,096; zero drops.

## 7. Native Sharded-SPSC Aggregate Scaling Audit
* **Classification:** CONSUMER-VALIDATED, RESOURCE-INSTRUMENTED, CAUSE NOT PROVEN
* **Uninstrumented Medians:**
  * 32 lanes: ~124.46M ops/sec
  * 64 lanes: ~164.66M ops/sec
  * 128 lanes: ~129.96M ops/sec
* **Resource-Instrumented Medians:**
  * 32 lanes: ~125.26M ops/sec (CPU ~5,913%, RSS 140,592 KB, Ctxt Sw 1,763, MaxQ 602, QFull 0)
  * 64 lanes: ~150.06M ops/sec (CPU ~9,809%, RSS 279,248 KB, Ctxt Sw 5,963, MaxQ 11,967, QFull 0)
  * 128 lanes: ~116.98M ops/sec (CPU ~7,547%, RSS 556,436 KB, Ctxt Sw 89,075, MaxQ 6,594, QFull 0)

## 8. Correctness and Integrity Evidence
All consumer-validated runs maintained strict sequence validation, checksum verification, and zero-loss guarantees across ring buffers.

## 9. Resource Telemetry
Resource utilization scales predictably with lane count up to 64 lanes, past which context switching overhead increases markedly at 128 lanes.

## 10. Repeatability Results
Throughput peaks consistently at 64 lanes across multiple runs, while the performance decline at 128 lanes is fully repeatable.

## 11. Limitations and Non-Claims
* **64 lanes** was the measured peak in both series.
* The **128-lane decline** was repeatable, but the **exact cause was not proven** (do not claim proven NUMA, SMT, physical-core, or scheduler causality).
* Do not claim zero contention.
* Do not describe synthetic native events as live-market packets.
* Do not describe local queue throughput as exchange throughput.
* Do not present historical PCAP numbers as newly reproduced.

## 12. Reproduction Notes
Compile with GCC (`-O3 -pthread -march=native`) and execute individual harness binaries under the `scripts/` and root directories against the verified PREEMPT_RT Linux kernel configuration.
