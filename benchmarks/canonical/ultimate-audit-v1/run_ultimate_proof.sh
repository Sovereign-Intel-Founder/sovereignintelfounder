#!/usr/bin/env bash
set -euo pipefail
RUN_ID="$(date +%Y-%m-%d)-ultimate-run-$(date +%H%M%S)"
OUT_DIR="benchmarks/results/ultimate-audit-v1/$RUN_ID"
mkdir -p "$OUT_DIR"
cd benchmarks/canonical/ultimate-audit-v1
echo "[*] Compiling Sovereign Ultimate Audit Binary..."
gcc -O3 -pthread benchmark.c -lm -o bench_exec
echo "[*] Capturing Binary SHA-256 Attestation..."
sha256sum bench_exec > binary_sha256.txt
echo "[*] Executing under Hardware Isolation..."
if command -v perf &> /dev/null; then
    perf stat -x, -e cycles,instructions,cache-misses,branch-misses -o perf_stats.csv taskset -c 0 ./bench_exec > stdout.log 2>&1
else
    taskset -c 0 ./bench_exec > stdout.log 2>&1
    echo "counter,value,unit" > perf_stats.csv
fi
cp stdout.log "../../../$OUT_DIR/stdout.log"
cp result_data.json "../../../$OUT_DIR/result.json"
cp binary_sha256.txt "../../../$OUT_DIR/binary_sha256.txt"
cp perf_stats.csv "../../../$OUT_DIR/perf_stats.csv"
cd - > /dev/null
cd "$OUT_DIR"
sha256sum result.json stdout.log binary_sha256.txt perf_stats.csv > sha256sums.txt
cd - > /dev/null
echo "[+] ULTIMATE AUDIT SEALED: $RUN_ID"
