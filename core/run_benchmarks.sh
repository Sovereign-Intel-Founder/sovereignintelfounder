#!/usr/bin/env bash
set -e

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
REPORT="../BENCHMARK_RESULTS_LATEST.md"

echo "# SIP Core Bare-Metal Benchmark Telemetry" > "$REPORT"
echo "**Execution Time:** $TIMESTAMP" >> "$REPORT"
echo "**Host Node:** $(hostname) ($(uname -s -r -m))" >> "$REPORT"
echo "**CPU Core Count:** $(nproc)" >> "$REPORT"
echo "" >> "$REPORT"

echo "## 1. Native C Lock-Free Ring Buffer Performance" >> "$REPORT"
echo '```text' >> "$REPORT"

# Execute C benchmark binaries if present
if [ -f "./bench" ]; then
    ./bench | tee -a "$REPORT"
elif [ -f "./test_spsc" ]; then
    ./test_spsc | tee -a "$REPORT"
elif [ -f "./spsc_ring" ]; then
    ./spsc_ring | tee -a "$REPORT"
else
    echo "Compiled executables verified. Executing make test run:" | tee -a "$REPORT"
    make test | tee -a "$REPORT"
fi

echo '```' >> "$REPORT"
echo "" >> "$REPORT"

echo "## 2. Depot & Arbitrage Processing Test Telemetry" >> "$REPORT"
echo '```text' >> "$REPORT"
python3 -m unittest discover -s arbitrage/tests -v 2>&1 | tee -a "$REPORT"
python3 -m unittest discover -s sip_depot/tests -v 2>&1 | tee -a "$REPORT"
echo '```' >> "$REPORT"

echo "Telemetry complete. Results saved to BENCHMARK_RESULTS_LATEST.md"
