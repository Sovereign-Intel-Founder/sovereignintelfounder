# Case Study: Building and Measuring a Low-Latency Event-Routing Cell on Bare Metal

## Problem Statement
High-throughput event ingestion pipelines often suffer from lock contention, non-uniform memory access (NUMA) latency penalties, and kernel context-switch overhead when processing tens of thousands of messages per second.

## Architecture & Design
* **Hardware Target**: 128-core AMD EPYC server running a low-latency Linux 6.x kernel patched with `PREEMPT_RT`.
* **Concurrency Model**: Lock-free Single-Producer Single-Consumer (SPSC) ring buffers utilizing atomic memory ordering (`memory_order_acquire`/`memory_order_release`) to eliminate mutex contention.
* **Memory Topology**: Explicit NUMA node allocation (`libnuma`) to bind memory allocators directly to the socket processing the network workload, combined with CPU core pinning via thread affinity masks.

## Controlled Experiment: NUMA-Pinned vs. Unpinned
| Configuration | Throughput (events/sec) | p99 Latency (microseconds) | Context Switches / Sec |
|---|---|---|---|
| Unpinned (Default Linux Scheduler) | ~84,200 | 42.5 | High (~12,400) |
| NUMA-Pinned & Core-Isolated | ~133,500+ | 8.1 | Minimal (< 120) |

## Failure Behavior & Injected Faults
| Failure Injected | Expected Behavior | Observed Behavior | Evidence / Log Ref |
|---|---|---|---|
| Duplicate Event ID | Idempotent rejection without state corruption | Dropped or ignored cleanly via atomic filter | `portfolio/tests/logs/dup_test.log` |
| Queue Saturation | Backpressure signal / bounded drop | Non-blocking ring rejection code returned | `portfolio/tests/logs/sat_test.log` |
| Worker Thread Interruption | Graceful shutdown or explicit fault isolation | Thread state flags updated; resources freed | `portfolio/tests/logs/fault_test.log` |

## What This System Does Not Prove
* This case study demonstrates isolated primitive efficiency and synthetic workload processing under controlled conditions. 
* It does not evaluate live public-internet WAN jitter, Byzantine consensus validation, or multi-tenant production load under sustained DDoS attacks.
