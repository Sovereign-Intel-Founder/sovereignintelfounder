#!/usr/bin/env bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root (sudo) to apply system-level performance tunings."
  exit 1
fi

echo "=================================================="
echo " SIP BARE-METAL NODE OPTIMIZATION: ashburn-baremetal"
echo "=================================================="

# 1. Set CPU Governor to Performance across all available cores (with busy-state handling)
echo "[+] Setting CPU governor to 'performance'..."
if command -v cpupower &> /dev/null; then
  cpupower frequency-set -g performance || echo "[!] cpupower notice: managed by hardware/pstate driver."
else
  for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$gov" ]; then
      echo "performance" > "$gov" 2>/dev/null || echo "[!] Note: Governor node $gov busy or locked, skipping."
    fi
  done
fi

# 2. Configure Transparent HugePages (THP) for shared memory / ring buffers
echo "[+] Configuring Transparent HugePages..."
if [ -f /sys/kernel/mm/transparent_hugepage/enabled ]; then
  echo "always" > /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null || true
fi
if [ -f /sys/kernel/mm/transparent_hugepage/defrag ]; then
  echo "madvise" > /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null || true
fi

# 3. Kernel Network & Buffer Tuning for Low-Latency Ingestion
echo "[+] Tuning kernel network parameters..."
sysctl -w net.core.rmem_max=134217728 > /dev/null || true
sysctl -w net.core.wmem_max=134217728 > /dev/null || true
sysctl -w net.core.rmem_default=67108864 > /dev/null || true
sysctl -w net.core.wmem_default=67108864 > /dev/null || true
sysctl -w net.core.netdev_max_backlog=250000 > /dev/null || true
sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864" > /dev/null || true
sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864" > /dev/null || true

# 4. Maximize File Descriptors for high-concurrency connections
echo "[+] Adjusting system limits..."
ulimit -n 1048576 2>/dev/null || true

echo "=================================================="
echo " NODE OPTIMIZATION COMPLETE: READY FOR HIGH-LOAD PIPELINES"
echo "=================================================="
