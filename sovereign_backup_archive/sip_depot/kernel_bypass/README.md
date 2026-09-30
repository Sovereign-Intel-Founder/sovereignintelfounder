# SIP Kernel-Bypass Ingestion Subsystem

Documentation and structural stubs for direct NIC packet ingestion via eBPF XDP and AF_XDP sockets.

## Design Goals
- Zero-copy packet delivery from network card to user-space UMEM.
- Elimination of standard Linux socket overhead and context switching.
- Integration with PREEMPT_RT kernel telemetry loops and core pinning.
