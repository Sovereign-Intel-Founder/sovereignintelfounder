#!/usr/bin/env bash
set -euo pipefail

RUN_ID="$(date +%Y-%m-%d)-run-$(date +%H%M%S)"
OUT_DIR="benchmarks/results/predictive-entropy-horizon-v1/$RUN_ID"
mkdir -p "$OUT_DIR"

cd benchmarks/canonical/predictive-entropy-horizon-v1
sha256sum bench_exec > binary_sha256.txt
./bench_exec > stdout.log 2>&1

cp stdout.log "../../../$OUT_DIR/stdout.log"
cp result_data.json "../../../$OUT_DIR/result.json"
cp binary_sha256.txt "../../../$OUT_DIR/binary_sha256.txt"
cd - > /dev/null

cd "$OUT_DIR"
sha256sum result.json stdout.log binary_sha256.txt > sha256sums.txt
cd - > /dev/null

echo "[+] Predictive entropy horizon run $RUN_ID executed and cryptographically sealed."
