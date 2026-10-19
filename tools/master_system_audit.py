#!/usr/bin/env python3
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.strip()}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    print("================================================================")
    print("     SOVEREIGN INTELLIGENCE PROTOCOL - MASTER EXHAUSTIVE AUDIT   ")
    print("================================================================")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    audit_data = {
        "timestamp": timestamp,
        "host": run_command(["hostname"]),
        "kernel": run_command(["uname", "-r"]),
        "all_listening_sockets": [],
        "established_connections": [],
        "systemd_services": {
            "active": [],
            "failed": [],
            "inactive": []
        },
        "port_registry_audit": {},
        "workspace_inventory": []
    }

    print("[*] Gathering all system-wide listening sockets...")
    ss_raw = run_command(["sudo", "ss", "-tulpn"])
    for line in ss_raw.splitlines():
        if "LISTEN" in line:
            audit_data["all_listening_sockets"].append(line)
            print(f"    [LISTEN] {line}")

    print("\n[*] Gathering established network connections...")
    ss_est = run_command(["sudo", "ss", "-tn", "state", "established"])
    for line in ss_est.splitlines():
        if "ESTAB" in line:
            audit_data["established_connections"].append(line)

    print("\n[*] Auditing all systemd service units...")
    systemd_raw = run_command(["systemctl", "list-units", "--type=service", "--all", "--no-legend"])
    for line in systemd_raw.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            unit_name = parts[0]
            load_state = parts[1]
            active_state = parts[2]
            sub_state = parts[3] if len(parts) > 3 else ""
            
            unit_info = {
                "unit": unit_name,
                "load": load_state,
                "active": active_state,
                "sub": sub_state
            }
            
            if active_state == "active":
                audit_data["systemd_services"]["active"].append(unit_info)
            elif active_state == "failed":
                audit_data["systemd_services"]["failed"].append(unit_info)
                print(f"    [!] FAILED SERVICE: {unit_name}")
            else:
                audit_data["systemd_services"]["inactive"].append(unit_info)

    print("\n[*] Loading and auditing Master Port Registry...")
    registry_path = Path("configs/sip_port_registry.json")
    if registry_path.exists():
        try:
            reg_content = json.loads(registry_path.read_text())
            ports_dict = reg_content.get("ports", {})
            
            for port_str, info in sorted(ports_dict.items(), key=lambda x: int(x[0])):
                comp_name = info.get("component", "Unknown")
                path_ref = info.get("path", "")
                
                # Check disk existence
                path_obj = Path(path_ref)
                exists = path_obj.exists() if not path_ref.startswith("REDIS") and not path_ref.startswith("ephemeral") else True
                
                # Check socket binding
                bound = any(f":{port_str} " in s or f":{port_str}" in s for s in audit_data["all_listening_sockets"])
                
                # Check active traffic
                has_traffic = any(f":{port_str}" in s for s in audit_data["established_connections"])
                
                # Extract PID / Command if bound
                pid = None
                cmdline = None
                if bound:
                    for s in audit_data["all_listening_sockets"]:
                        if f":{port_str}" in s and "pid=" in s:
                            try:
                                pid_part = [p for p in s.split() if "pid=" in p][0]
                                pid = pid_part.split("pid=")[1].split(",")[0].strip()
                                cmdline = Path(f"/proc/{pid}/cmdline").read_text().replace("\x00", " ")
                            except Exception:
                                pass

                port_audit_record = {
                    "port": port_str,
                    "component": comp_name,
                    "path_reference": path_ref,
                    "exists_on_disk": exists,
                    "is_bound": bound,
                    "has_established_traffic": has_traffic,
                    "pid": pid,
                    "command_line": cmdline
                }
                
                audit_data["port_registry_audit"][port_str] = port_audit_record
                print(f"    [PORT {port_str}] {comp_name} -> Bound: {bound}, Traffic: {has_traffic}, Disk: {exists}")
        except Exception as e:
            print(f"    [ERROR] Failed to parse port registry: {e}")
    else:
        print("    [!] Warning: configs/sip_port_registry.json not found.")

    print("\n[*] Scanning workspace repository files...")
    for p in Path(".").rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            audit_data["workspace_inventory"].append(str(p))

    output_filename = f"configs/master_exhaustive_audit_report_{timestamp}.json"
    Path("configs").mkdir(exist_ok=True)
    Path(output_filename).write_text(json.dumps(audit_data, indent=2))
    
    # Also overwrite a stable symlink/latest copy for quick inspection
    Path("configs/master_exhaustive_audit_latest.json").write_text(json.dumps(audit_data, indent=2))

    print("================================================================")
    print(f" AUDIT COMPLETE. Report saved to: {output_filename}")
    print("================================================================")

if __name__ == "__main__":
    main()
