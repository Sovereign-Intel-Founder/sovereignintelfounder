#!/bin/bash
set -eo pipefail

echo "================================================================"
echo " Sovereign Intelligence Protocol - Full Ecosystem Build Suite"
echo "================================================================"

# 1. Run Core Hardening Test Harness
echo "[*] Step 1: Running deployment suite validation..."
bash scripts/test_harness.sh

# 2. Run Cryptographic Handoff Validation
echo "[*] Step 2: Executing cryptographic envelope handoff test..."
python3 sip_remote_handoff/handoff_validator.py

# 3. Run SQLite WAL Concurrency Benchmark
echo "[*] Step 3: Executing SQLite WAL high-throughput benchmark..."
python3 benchmarks/wal_concurrency_test.py

echo "================================================================"
echo "[✓] FULL PROTOCOL ECOSYSTEM BUILT, HARDENED, AND VERIFIED."
echo "================================================================"
