#!/bin/bash
echo "[*] Stopping Sovereign Intelligence Protocol pipeline..."
sudo pkill -f sovereign_live_engine
pkill -f live_feeder.py
rm -f /dev/shm/sovereign_live_ring
echo "[*] Pipeline halted and shared memory cleaned."
