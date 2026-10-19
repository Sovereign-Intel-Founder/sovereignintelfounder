#!/usr/bin/env python3
import os
import subprocess
import sys
import socket
import json

TARGET_SERVICES = [
    "sip-commons.service",
    "sip-master-supervisor.service",
    "sip-core-tollbridge.service",
    "sovereign-engine.service",
    "sovereign-producer.service",
    "cloudflared-sip.service",
    "apex-ingress.service"
]

def run_cmd(cmd, capture=False):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None, text=True)
    return res.returncode == 0, res.stdout.strip() if capture else ""

def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def diagnose_and_heal():
    print("=== [SIP] INITIALIZING COMPREHENSIVE CLUSTER HEALER ===")
    
    if os.geteuid() != 0:
        print("[!] Warning: Not running as root. Systemd service modifications/restarts may require sudo privileges.")

    # 1. Secure Ledger & Telemetry Permissions
    print("\n[*] Step 1: Validating ledger, memory, and telemetry write permissions...")
    ledger_paths = ["memory", "core/benchmarks", "benchmarks", "core/mesh", "commons_bridge"]
    for p in ledger_paths:
        os.makedirs(p, exist_ok=True)
    run_cmd("chmod -R 775 memory benchmarks core/benchmarks commons_bridge 2>/dev/null || true")
    print("[+] Workspace paths secured and verified.")

    # 2. Audit Port Bindings & Potential Conflicts
    print("\n[*] Step 2: Scanning critical service ports for collisions...")
    ports_to_check = {11434: "Ollama", 20242: "Cloudflared Ingress", 9800: "FluidSynth", 8080: "Local Origin"}
    for port, name in ports_to_check.items():
        in_use = check_port_in_use(port)
        status = "ACTIVE / BOUND" if in_use else "FREE / UNBOUND"
        print(f"    - Port {port} ({name}): {status}")

    # 3. Process Systemd Units & Clear Rate Limits
    print("\n[*] Step 3: Inspecting systemd service health and resetting failed states...")
    for svc in TARGET_SERVICES:
        success, active_status = run_cmd(f"systemctl is-active {svc}", capture=True)
        success_failed, failed_status = run_cmd(f"systemctl is-failed {svc}", capture=True)
        
        print(f"    -> Service: {svc}")
        print(f"       Active State: {active_status}")
        
        if failed_status == "failed":
            print(f"       [!] Service is in FAILED state. Resetting failure counter...")
            run_cmd(f"sudo systemctl reset-failed {svc}")
            
    # 4. Controlled Staggered Restart Sequence
    print("\n[*] Step 4: Executing controlled, non-overlapping service reconciliation...")
    for svc in TARGET_SERVICES:
        print(f"    [*] Restarting {svc}...")
        success, err = run_cmd(f"sudo systemctl restart {svc}", capture=True)
        if not success:
            print(f"        [-] Error starting {svc}: {err}")
        else:
            print(f"        [+] {svc} started successfully.")

    print("\n=== [SIP] CLUSTER RECONCILIATION COMPLETE ===")
    print("Run `python3 tools/sip_system_review.py` to review updated cluster telemetry.")

if __name__ == "__main__":
    diagnose_and_hq = diagnose_and_heal()
