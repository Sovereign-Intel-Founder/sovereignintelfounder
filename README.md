# Sovereign Intelligence Protocol (SIP)

An elite, 100% live, bare-metal low-latency Solana systems engineering pipeline designed for real-time mainnet transaction ingestion, temporal delta tracking, and dynamic Jito bundle tipping.

## Architecture Overview

SIP breaks away from traditional node bloat and simulation placeholders by implementing a decoupled, zero-copy inter-process communication model:

* **High-Performance C Engine:** Handles raw byte parsing, bitstream validation, toll-bridge filtering, and mesh routing. Pinned to dedicated silicon with real-time scheduling priority.
* **Resilient Python Wire Feeder:** Maintains an autonomous WebSocket connection to Solana mainnet RPCs with an exponential backoff watchdog, pushing raw slots straight into shared memory.
* **POSIX Shared Memory Ring Buffer:** Zero-copy lock-free ring buffer (`/dev/shm/sovereign_live_ring`) engineered for microsecond-scale cross-process throughput.

## Low-Latency Hardening & Determinism

* **Core Isolation & Pinning:** Execution threads are explicitly pinned to physical CPU cores via `pthread_setaffinity_np`.
* **Real-Time Priority:** Engages `SCHED_FIFO` priority 99 and locks physical RAM via `mlockall` to eliminate paging latency.
* **NUMA Optimization:** Shared memory buffers are explicitly bound to NUMA Node 0 memory controllers using `mbind`.
* **Unified Temporal Domain:** High-resolution monotonic nanosecond timing (`clock_gettime(CLOCK_MONOTONIC)`) tracks exact wire-to-execution deltas.
