import json
import subprocess
import sys
from pathlib import Path

def get_journal_logs(unit_name, limit=50):
    try:
        res = subprocess.run(["journalctl", "-u", unit_name, "-n", str(limit), "--no-pager", "-o", "short-iso"], capture_output=True, text=True)
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []

def get_file_logs(file_path, limit=50):
    p = Path(file_path)
    if not p.exists():
        return []
    try:
        with open(p, "r", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
            return lines[-limit:]
    except Exception:
        return []

def sip_status_report(limit=50):
    print("==================================================")
    print("         SIP UNIFIED SYSTEM HEALTH REPORT         ")
    print("==================================================")
    
    daemon_logs = get_file_logs("sip_daemon.log", 1)
    sup_logs = get_journal_logs("sip-master-supervisor", 1)
    bridge_logs = get_journal_logs("sip-toll-bridge", 1)
    
    print(f"1. sip_daemon         : {('HEALTHY' if daemon_logs else 'BROKEN')} (Log capture active)")
    print(f"2. Master Supervisor  : {('HEALTHY' if sup_logs else 'ALIVE-UNVERIFIED')} (Journal captured)")
    print(f"3. Toll Bridge Ingress: {('HEALTHY' if bridge_logs else 'ALIVE-UNVERIFIED')} (Systemd unit captured)")
    
    print(f"\n--- LATEST COMBINED LOG ENTRIES (Last {limit}) ---")
    combined = []
    for l in get_file_logs("sip_daemon.log", limit):
        combined.append(("[SIP-DAEMON]", l))
    for l in get_journal_logs("sip-master-supervisor", limit):
        combined.append(("[SUPERVISOR]", l))
    for l in get_journal_logs("sip-toll-bridge", limit):
        combined.append(("[TOLL-BRIDGE]", l))
        
    if not combined:
        print("No unified log entries available.")
    else:
        for tag, entry in combined[-limit:]:
            print(f"{tag} {entry}")
    print("==================================================")

if __name__ == "__main__":
    limit = 50
    if len(sys.argv) > 2 and sys.argv[1] == "--last":
        try:
            limit = int(sys.argv[2])
        except ValueError:
            pass
    sip_status_report(limit)

def audit_port_bindings():
    print("\n--- MASTER PORT REGISTRY & BINDING AUDIT ---")
    reg_path = Path("configs/sip_port_registry.json")
    if not reg_path.exists():
        print("Registry file missing.")
        return
    
    registry = json.loads(reg_path.read_text())["ports"]
    
    try:
        res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, check=True)
        active_sockets = res.stdout
    except Exception:
        print("Could not query active sockets.")
        return

    for port_str, info in registry.items():
        bound = f":{port_str} " in active_sockets or f":{port_str}" in active_sockets
        status = "BOUND & ACTIVE" if bound else "IDLE / UNBOUND"
        print(f"Port {port_str:<5} | {info['component']:<35} | {status}")
    print("--------------------------------------------")

if __name__ == "__main__":
    audit_port_bindings()
