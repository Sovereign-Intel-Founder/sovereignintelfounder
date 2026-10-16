#!/usr/bin/env python3
import json
import socket
import subprocess
from pathlib import Path
import sqlite3

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=0.8):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def main():
    print("==================================================")
    print("          SIP COMPREHENSIVE CLUSTER HEALTH        ")
    print("==================================================")
    
    # 1. Manifest & Component Parsing
    manifest_path = Path("system_manifest.json")
    if manifest_path.exists():
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        print(f"[+] Manifest Status: {manifest.get('status', 'UNKNOWN')}")
        components = manifest.get("components", [])
        print(f"[+] Registered Components in Manifest: {len(components)}")
        for comp in components:
            print(f"    - {comp.get('name', 'Unknown')} ({comp.get('type', 'service')}) -> Status: {comp.get('status', 'ACTIVE')}")
    else:
        print("[-] Error: system_manifest.json not found!")

    # 2. Service & Port Bindings Check
    services = [
        {"name": "Uvicorn Ingress Server", "host": "127.0.0.1", "port": 8003},
        {"name": "SIP Daemon (Worker)", "host": "0.0.0.0", "port": 9872},
        {"name": "Solana Test Validator", "host": "127.0.0.1", "port": 8000},
    ]

    print("\n--- Network Endpoints & Ports ---")
    for svc in services:
        alive = check_port(svc["host"], svc["port"])
        status = "\033[92m[ACTIVE]\033[0m" if alive else "\033[91m[DOWN]\033[0m"
        print(f" {status} {svc['name']} -> {svc['host']}:{svc['port']}")

    # 3. Process Monitoring via pgrep
    print("\n--- Background Daemon Processes ---")
    daemons = ["toll_bridge_daemon.py", "solana-maintenance-daemon.py", "sip_watchdog.py"]
    for d in daemons:
        res = subprocess.run(["pgrep", "-f", d], capture_output=True, text=True)
        if res.stdout.strip():
            pids = res.stdout.strip().replace("\n", ", ")
            print(f" \033[92m[RUNNING]\033[0m {d} (PID(s): {pids})")
        else:
            print(f" \033[91m[STOPPED]\033[0m {d}")

    # 4. Storage & Ledger Metrics + Last 10 Samples
    ledger_path = Path("sip_ledger.db")
    print("\n--- Persistence & Ledger Samples ---")
    if ledger_path.exists():
        size = ledger_path.stat().st_size
        print(f" \033[92m[OK]\033[0m Ledger database found ({size} bytes)")
        try:
            conn = sqlite3.connect(ledger_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"     Active Tables: {tables if tables else 'None (empty schema)'}")
            
            for table in tables:
                print(f"\n   --- Last 10 records from table: [{table}] ---")
                try:
                    cursor.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 10;")
                    rows = cursor.fetchall()
                    if rows:
                        for idx, row in enumerate(rows, 1):
                            print(f"     {idx:2d}. {row}")
                    else:
                        print("     (Table is currently empty)")
                except Exception as table_err:
                    print(f"     Could not query table {table}: {table_err}")
            conn.close()
        except Exception as e:
            print(f"     \033[93m[WARN]\033[0m Could not query ledger: {e}")
    else:
        print(" \033[91m[WARNING]\033[0m Ledger database missing!")
    print("==================================================")

if __name__ == "__main__":
    main()
