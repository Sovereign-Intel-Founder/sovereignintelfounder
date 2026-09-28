## Test Environment & Reproducibility

The workload matrix and saturation benchmarks were executed on a dedicated bare-metal research server with the following specifications:

- **Host Location:** Ashburn, VA (LeaseWeb)
- **Processor:** AMD EPYC (128 logical cores)
- **Memory:** 728 GB RAM
- **OS Kernel:** Linux 6.x (patched with PREEMPT_RT)
- **Execution Scope:** Single-host synthetic workload harness (local loopback interface)

### Verification Commands
To inspect the environment telemetry and reproduce local harness validation, run:

    uname -r
    lscpu | grep -E "Model name|Core\(s\) per socket|CPU\(s\):"
    free -h
    gcc --version
    git rev-parse HEAD
