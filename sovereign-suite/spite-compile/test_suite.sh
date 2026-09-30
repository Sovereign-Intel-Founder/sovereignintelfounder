#!/bin/bash
set -e

echo "[*] Building latest release binary for stress testing..."
cargo build --release > /dev/null 2>&1

ARMORER="./target/release/spite-compile"
PASS_COUNT=0
FAIL_COUNT=0

# Setup sandbox environment
mkdir -p ./test_sandbox
cp /bin/ls ./test_sandbox/bin_ls
cp /bin/cat ./test_sandbox/bin_cat
cp /bin/grep ./test_sandbox/bin_grep
echo "NOT_AN_ELF" > ./test_sandbox/corrupt_file

# Test 1: Batch Armoring Multiple Binaries
echo -n "[-] Testing [Batch Armoring Multiple Binaries]... "
if for f in ./test_sandbox/bin_*; do "$ARMORER" "$f" > /dev/null 2>&1 || exit 1; done; then
    echo "PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "FAILED"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Test 2: Negative input defense (Corrupt files)
echo -n "[-] Testing [Graceful Rejection of Corrupt Files]... "
if ! "$ARMORER" "./test_sandbox/corrupt_file" > /dev/null 2>&1; then
    echo "PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "FAILED (Accepted invalid file)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Test 3: Concurrent execution stress test (10 parallel jobs)
echo -n "[-] Testing [Concurrent Parallel Stress Run]... "
for i in {1..10}; do
    "$ARMORER" "./test_sandbox/bin_ls" > /dev/null 2>&1 &
done
wait

if [ -f "./test_sandbox/bin_ls.armored" ]; then
    echo "PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "FAILED (Concurrency artifact missing)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Cleanup sandbox
rm -rf ./test_sandbox

echo "=========================================="
echo "Enterprise Test Results: $PASS_COUNT Passed, $FAIL_COUNT Failed"
echo "=========================================="

if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi
