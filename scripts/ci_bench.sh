#!/usr/bin/env bash
set -eo pipefail

echo "==> Running Automated Latency Regression Check..."

# Check context-switching baseline
SCHED_LATENCY=$(perf bench sched pipe -l 100000 2>&1 | awk '/ops\/sec/ {print $1}')
echo "Measured Scheduling Throughput: $SCHED_LATENCY ops/sec"

# Enforce throughput threshold (>100,000 ops/sec)
if [ "$SCHED_LATENCY" -lt 100000 ]; then
  echo "PERFORMANCE REGRESSION DETECTED: Scheduling throughput dropped below threshold."
  exit 1
fi

echo "==> Baseline Latency Verification PASSED."
