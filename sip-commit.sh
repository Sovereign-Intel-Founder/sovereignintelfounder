#!/bin/bash
# Permanent automation script for Sovereign Intelligence Protocol
if [ -z "$1" ]; then
    echo "Usage: ./sip-commit.sh \"your commit message\""
    exit 1
fi

echo "[*] Staging core infrastructure safely..."
git add -u
git add sovereign_intel/ core/ ebpf/ fpga/ manifests/ scripts/ .github/ *.md *.c *.cpp *.py *.sh *.h *.json

echo "[*] Committing..."
git commit -m "$1"

echo "[*] Pushing to remote..."
git push origin main
echo "[+] Done. Repository synchronized cleanly."
