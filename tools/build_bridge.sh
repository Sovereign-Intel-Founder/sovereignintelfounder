#!/bin/bash
set -e

echo "[*] Compiling SIP Shared Memory Bridge & Hardened Core..."
gcc -O3 -std=c11 -I. -fPIE -pie -fvisibility=hidden -flto core_logic.c sip_bridge.c -o build/sip_bridge -lrt -lpthread
strip --strip-all --remove-section=.comment --remove-section=.note.gnu.build-id build/sip_bridge

echo "[+] SIP Shared Memory Bridge successfully built at build/sip_bridge"
