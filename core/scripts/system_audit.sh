#!/bin/bash
echo "========================================================="
echo "   SOVEREIGN INTELLIGENCE PROTOCOL: RUNTIME AUDIT        "
echo "========================================================="

echo -e "\n[1] ACTIVE PROCESSES & THREADS (Core Engine / Routing / Benchmarks):"
ps -ef | grep -E "tollbridge|sip_|benchmark|native|spsc|xdp" | grep -v grep || echo "No matching active processes found."

echo -e "\n[2] SHARED MEMORY & IPC (POSIX /dev/shm & System V):"
ls -la /dev/shm
ipcs -m

echo -e "\n[3] LOADED eBPF MAPS & PROGRAMS (Kernel Bypass / Rings):"
if command -v bpftool &> /dev/null; then
    echo "--- eBPF Maps ---"
    bpftool map show
    echo "--- eBPF Programs ---"
    bpftool prog show
else
    echo "bpftool not found in path."
fi

echo -e "\n[4] XDP & NETWORK INTERFACE BYPASS STATUS:"
ip link show | grep -E "xdp|gsk|eth|enp" -A 2

echo -e "\n[5] ACTIVE SOCKETS & LISTENING PORTS (Toll Bridge / RPC):"
ss -tulpn | grep -E "LISTEN|ESTAB" || netstat -tulpn 2>/dev/null || echo "Socket check complete."

echo -e "\n[6] ACTIVE SQLITE WAL & SHARED DATABASES:"
find /home/joshua445 -name "*.db-wal" -o -name "*.db-shm" -o -name "*.db" 2>/dev/null || echo "No active database files found in workspace."

echo -e "\n========================================================="
echo "   AUDIT COMPLETE - REVIEW METRICS ABOVE                 "
echo "========================================================="
