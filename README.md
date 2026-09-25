# Sovereign Intelligence Protocol — AF_XDP Native Kernel Bypass Engine

High-throughput, ultra-low-latency packet ingestion pipeline built for bare-metal systems. Bypasses the Linux network stack entirely via native eBPF driver hooks and POSIX shared memory ring buffers.

## Architectural Breakthrough: mlx5_core Native Attachment
Mellanox `mlx5` drivers enforce strict validation rules on UMEM memory alignment, ring sizing, and BPF dispatcher attachments. To maintain sub-microsecond processing without falling back to generic SKB mode, the engine implements a hybrid attachment paradigm:

1. **Native Driver Loading:** The eBPF program (`sovereign_ebpf.o`) is attached natively to the NIC via `bpf_xdp_attach()` in hardware driver mode (`XDP_FLAGS_DRV_MODE`).
2. **Program Load Inhibition:** The AF_XDP socket is created via `libxdp` with the explicit `XSK_LIBXDP_FLAGS_INHIBIT_PROG_LOAD` bit flag set.
3. **UMEM Direct Mapping:** `libxdp` negotiates queue ring structures directly with `mlx5_core` while strictly blocked from overwriting the pre-attached native eBPF hook.

## Telemetry & Benchmark Baselines
| Metric | Measured Baseline | Target |
| :--- | :--- | :--- |
| **Peak Event Throughput** | > 133,000 events / sec | 250,000 events / sec |
| **Sustained Load Run** | > 3.35M events / 75 seconds | Continuous Line-Rate |
| **Memory Allocation** | Zero-copy page-aligned UMEM | Zero-copy |
| **Attachment Mode** | Native Driver (`mlx5`) | Native Driver |

## Current Status
* **[x] Native Driver Attachment:** Bypassed `mlx5_core` validation rejections.
* **[x] Socket Binding:** Established stable zero-copy AF_XDP socket initialization.
* **[x] Hardware Hijack Verified:** Confirmed zero-copy frame redirection from NIC to user-space UMEM.
* **[ ] Active Ingestion Ring:** Wiring zero-copy `poll()` consumer ring batching.
