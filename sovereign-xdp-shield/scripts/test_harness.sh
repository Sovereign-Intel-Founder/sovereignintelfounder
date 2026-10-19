#!/bin/bash
set -eo pipefail

echo "=================================================="
echo " Sovereign Intelligence Protocol - Test Harness"
echo "=================================================="

FAILED=0

# Test 1: Script Syntax Validation (Bash Static Analysis)
echo -n "[*] Running static syntax analysis on deployment suite... "
if bash -n scripts/deploy_core.sh && bash -n scripts/deploy_vps.sh && bash -n scripts/deploy_edge.sh; then
    echo "[PASSED]"
else
    echo "[FAILED]"
    ((FAILED++))
fi

# Test 2: Execution Permission Checks
echo -n "[*] Verifying script execution permissions... "
if [ -x "scripts/deploy_core.sh" ] && [ -x "scripts/deploy_vps.sh" ] && [ -x "scripts/deploy_edge.sh" ]; then
    echo "[PASSED]"
else
    echo "[FAILED]"
    ((FAILED++))
fi

# Test 3: Documentation Sync Check
echo -n "[*] Verifying multi-tier documentation registry... "
if [ -f "docs/NODE_TIERS.md" ]; then
    echo "[PASSED]"
else
    echo "[FAILED]"
    ((FAILED++))
fi

echo "=================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "[✓] ALL HARDENING TESTS PASSED ACROSS THE BOARD."
    exit 0
else
    echo "[x] Test Suite Failed with $FAILED error(s)."
    exit 1
fi
