#!/usr/bin/env bash
set -eo pipefail

echo "==> Running Automated Latency Regression Check..."

# Run pipe benchmark and extract integer throughput
RAW_OPS=$(perf bench sched pipe -l 50000 2>&1 | grep "ops/sec" | awk '{print $1}' || true)

# Default to 0 if empty
SCHED_LATENCY=${RAW_OPS:-0}

echo "Measured Scheduling Throughput: $SCHED_LATENCY ops/sec"

if [ "$SCHED_LATENCY" -lt 100000 ]; then
  echo "PERFORMANCE REGRESSION DETECTED: Scheduling throughput ($SCHED_LATENCY ops/sec) below 100,000 threshold."
  exit 1
fi

echo "==> Baseline Latency Verification PASSED."
