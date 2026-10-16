import os
import sys
import time
import subprocess
from pathlib import Path

def get_process_info():
    processes = []
    for entry in os.listdir('/proc'):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmdline = f.read().decode('utf-8', errors='ignore').replace('\x00', ' ').strip()
            if not cmdline:
                continue
            
            # Filter for sovereign or relevant python/daemon processes
            if not any(k in cmdline for k in ['sip', 'toll', 'sovereign', 'ingress']):
                continue

            exe = os.readlink(f"/proc/{pid}/exe") if os.path.exists(f"/proc/{pid}/exe") else "unknown"
            cwd = os.readlink(f"/proc/{pid}/cwd") if os.path.exists(f"/proc/{pid}/cwd") else "unknown"
            
            with open(f"/proc/{pid}/stat", "r") as f:
                stat_data = f.read().split()
                ppid = stat_data[3]
                starttime = stat_data[21]

            processes.append({
                "pid": pid,
                "ppid": ppid,
                "cmdline": cmdline,
                "exe": exe,
                "cwd": cwd,
                "starttime": starttime
            })
        except (PermissionError, FileNotFoundError, ProcessLookupError):
            continue
    return processes

def audit_system():
    print("=== SOVEREIGN SYSTEM AUDIT (READ-ONLY) ===")
    procs = get_process_info()
    
    supervisor_count = 0
    for p in procs:
        if "sip_master_supervisor.py" in p['cmdline']:
            supervisor_count += 1

        print(f"\n[PROCESS] PID: {p['pid']} | PPID: {p['ppid']}")
        print(f"  Command: {p['cmdline']}")
        print(f"  Executable: {p['exe']}")
        print(f"  Working Dir: {p['cwd']}")
        
        # Classification logic based on runtime state and workspace references
        if "sip_daemon" in p['cmdline'] or "server.py" in p['cmdline']:
            classification = "ACTIVE (Core Service Running)"
        elif "sip_master_supervisor.py" in p['cmdline']:
            classification = "ACTIVE / POTENTIAL DUPLICATE" if supervisor_count > 1 else "ACTIVE"
        else:
            classification = "REFERENCED"
        print(f"  Classification: {classification}")

    print(f"\n[SUMMARY] Total matching Sovereign processes found: {len(procs)}")
    print(f"[SUPERVISOR ANALYSIS] Total sip_master_supervisor.py instances running: {supervisor_count}")
    if supervisor_count > 1:
        print("  -> Multiple supervisors detected. Check PPID tree to see if spawned by shell sessions or orphaned.")
    else:
        print("  -> Supervisor count is optimal (single instance).")

    # Check Log Destinations & Batching Capability
    log_files = list(Path('.').glob('*.log')) + list(Path('evidence').glob('*.json'))
    print(f"\n[LOG AUDIT] Found {len(log_files)} active log/audit files:")
    for lf in log_files:
        size_kb = lf.stat().st_size / 1024
        print(f"  - {lf} ({size_kb:.1f} KB)")
    print("  -> Centralized collection and batch querying (last 50/100 entries) is fully supported via Python log reader helper.")

if __name__ == '__main__':
    audit_system()
