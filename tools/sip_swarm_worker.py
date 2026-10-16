import os
import subprocess
import time
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path

SERVICES_TO_MONITOR = [
    {"name": "sip_bridge", "pattern": "sip_bridge"},
    {"name": "toll_bridge_daemon", "pattern": "toll_bridge_daemon.py"},
    {"name": "solana_maintenance", "pattern": "solana-maintenance-daemon.py"},
    {"name": "sip_watchdog", "pattern": "sip_watchdog.py"}
]

ENDPOINTS = [
    {"name": "Uvicorn Ingress", "url": "http://127.0.0.1:8003"},
    {"name": "SIP Worker Daemon", "url": "http://127.0.0.1:9872"},
    {"name": "Solana Validator", "url": "http://127.0.0.1:8000"}
]

def log_to_ledger(node_id, status, proof_hash):
    conn = sqlite3.connect("sip_ledger.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO execution_ledger (timestamp, node_id, slot, proof_hash, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (time.time(), node_id, 0, proof_hash, status))
    conn.commit()
    conn.close()

def check_processes():
    for service in SERVICES_TO_MONITOR:
        cmd = f"pgrep -f '{service['pattern']}'"
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        if not res.stdout.strip():
            print(f"[!] SWARM ALERT: Service down -> {service['name']}")
            log_to_ledger(service['name'], "DOWN", "ANOMALY_PROCESS_MISSING")
        else:
            print(f"[OK] Service active -> {service['name']}")

def check_endpoints():
    for ep in ENDPOINTS:
        try:
            req = urllib.request.Request(ep['url'], headers={'User-Agent': 'SIP-Swarm-Worker'})
            with urllib.request.urlopen(req, timeout=2) as response:
                print(f"[OK] Endpoint active -> {ep['name']} ({response.status})")
        except Exception as e:
            print(f"[!] SWARM ALERT: Endpoint unreachable -> {ep['name']} ({e})")
            log_to_ledger(ep['name'], "UNREACHABLE", str(e))

def swarm_sweep():
    print(f"\n--- SWARM DIAGNOSTIC SWEEP @ {time.ctime()} ---")
    check_processes()
    check_endpoints()
    print("---------------------------------------------")

if __name__ == "__main__":
    print("[+] SIP Swarm Diagnostic Worker initialized. Running continuous sweeps...")
    while True:
        try:
            swarm_sweep()
        except Exception as e:
            print(f"[!] Swarm sweep error: {e}")
        time.sleep(30)
