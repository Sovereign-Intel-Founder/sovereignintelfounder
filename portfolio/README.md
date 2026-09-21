# High-Performance Systems Engineering Showcase

This directory contains focused systems-engineering experiments and benchmarking components developed as part of Sovereign Intelligence Protocol research. Each component is presented independently to demonstrate specific skills in low-latency programming, Linux systems work, memory locality, concurrency design, and performance measurement.

These files are **standalone demonstrations and research components**. They are not presented as one production runtime, and each section identifies what the code currently demonstrates.

## Showcase Components

* **AF_XDP socket and kernel-bypass probe** (`src/af_xdp_packet_bypass.c`): validates creation of an AF_XDP raw socket when the host provides the required capabilities and interface configuration. It is a socket-level probe, not a complete packet-ingestion pipeline.
* **Cache-aligned SPSC ring structure** (`src/lockfree_spsc_ring.c`): demonstrates atomic head/tail fields, cache-line padding, fixed-size slots, and false-sharing-aware layout. It is a structural concurrency primitive; throughput requires a separate producer/consumer benchmark.
* **NUMA-local allocation** (`src/numa_aware_alloc.c`): demonstrates allocation and release of memory on a selected NUMA node when NUMA support is available.
* **Thread affinity and NUMA locality** (`src/numa_core_pin.c`): demonstrates pinning a worker thread to a selected CPU and reporting its NUMA node. Production use requires checking affinity-call results and validating the host topology.
* **Cycle-counter measurement probes** (`src/latency_benchmark.c`, `src/rdtsc_telemetry.c`): demonstrate reading the x86 timestamp counter around a bounded operation. Results are reported in cycles; converting them to time requires calibrated CPU-frequency and serialization methodology.

## Evidence and Status

Benchmark results, hardware context, methodology, and limitations are documented separately. A component should be treated as a demonstration or research primitive unless its documentation includes a reproducible build command, workload, measurement boundary, raw output, and known limitations.

