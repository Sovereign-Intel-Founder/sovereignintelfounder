# Evidence & Reproducibility Index

This index maps each showcase component and research area to its source path, exact execution command, environment, empirical proof, and stated limitations.

## Active Colosseum Submission
| Capability | Repository path | Evidence file | Exact command | Workload/environment | What it proves | Limitations |
|---|---|---|---|---|---|---|
| Competition Entry | `coliseum-submission/` | `coliseum-submission/README.md` | `cat coliseum-submission/README.md` | Colosseum evaluation environment | Complete architecture and benchmark claims under active review | Preserved as-is; pending final judging |

## Concurrency & Shared Memory
| Capability | Repository path | Evidence file | Exact command | Workload/environment | What it proves | Limitations |
|---|---|---|---|---|---|---|
| Lock-Free SPSC Ring | `portfolio/src/lockfree_spsc_ring.c` | `portfolio/src/lockfree_spsc_ring.c` | `gcc -O3 portfolio/src/lockfree_spsc_ring.c -lpthread -o ring_test && ./ring_test` | 128-core AMD EPYC, isolated core | Atomic head/tail progression without mutex contention | Standalone primitive demonstration |

## NUMA & CPU Affinity
| Capability | Repository path | Evidence file | Exact command | Workload/environment | What it proves | Limitations |
|---|---|---|---|---|---|---|
| NUMA Node Allocation | `portfolio/src/numa_aware_alloc.c` | `portfolio/src/numa_aware_alloc.c` | `gcc -O3 portfolio/src/numa_aware_alloc.c -lnuma -o numa_test && ./numa_test` | Multi-socket AMD EPYC, Linux PREEMPT_RT | Physical node memory allocation and topology binding | API demonstration probe |

## Low-Latency Measurement & Telemetry
| Capability | Repository path | Evidence file | Exact command | Workload/environment | What it proves | Limitations |
|---|---|---|---|---|---|---|
| RDTSC Cycle Counter | `portfolio/src/rdtsc_telemetry.c` | `portfolio/src/rdtsc_telemetry.c` | `gcc -O3 portfolio/src/rdtsc_telemetry.c -o rdtsc_test && ./rdtsc_test` | Pinned core, performance governor | Raw CPU cycle deltas for execution tracing | Measures cycles, requires frequency scaling calibration for real-time |

## Network & Kernel-Bypass Experiments
| Capability | Repository path | Evidence file | Exact command | Workload/environment | What it proves | Limitations |
|---|---|---|---|---|---|---|
| AF_XDP Socket Bypass | `portfolio/src/af_xdp_packet_bypass.c` | `portfolio/src/af_xdp_packet_bypass.c` | `gcc -O3 portfolio/src/af_xdp_packet_bypass.c -lbpf -o xdp_test` | Linux network interface, root context | Raw socket creation and packet extraction probe | Socket-level prototype / demonstration |

## Benchmark & Failure Testing
| Capability | Repository path | Evidence file | Exact command | Workload/environment | What it proves | Limitations |
|---|---|---|---|---|---|---|
| Latency Test Harness | `portfolio/src/latency_benchmark.c` | `portfolio/src/latency_benchmark.c` | `gcc -O3 portfolio/src/latency_benchmark.c -o bench_test && ./bench_test` | Bare-metal test harness | Synthetic event throughput and execution timing | Synthetic workload simulation |
