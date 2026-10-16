#!/usr/bin/env bash
set -euo pipefail

RUN_ID="$(date +%Y-%m-%d)-run-$(date +%H%M%S)"
OUT_DIR="benchmarks/results/spsc-bounded-v1/$RUN_ID"
mkdir -p "$OUT_DIR"

cd benchmarks/canonical/spsc-bounded-v1
./bench_exec > stdout.log 2>&1
cp stdout.log "../../../$OUT_DIR/stdout.log"
cp result_data.json "../../../$OUT_DIR/result.json"
cd - > /dev/null

cd "$OUT_DIR"
sha256sum result.json stdout.log > sha256sums.txt
cd - > /dev/null

echo "[+] Real compiled SPSC benchmark run $RUN_ID executed and hashed successfully."
