import os
import ast
import re

TARGET_DIR = "/home/joshua445/tollbridge_system"

def audit_and_repair_file(filepath):
    print(f"[*] Auditing: {os.path.basename(filepath)}")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    cleaned_lines = []
    removed_count = 0
    fastapi_app_count = 0

    for line in lines:
        stripped = line.strip()
        # Filter out markdown artifacts, URL documentation spam, and browser text blocks
        if ('tiangolo.com' in line or 
            ('](' in stripped and 'http' in stripped) or 
            ('[FastAPI docs' in line) or
            (stripped.startswith('[') and ']' in stripped and 'http' in line)):
            removed_count += 1
            continue

        # Track and deduplicate excessive FastAPI instantiations if found outside imports/classes
        if 'app = FastAPI()' in stripped:
            fastapi_app_count += 1
            if fastapi_app_count > 1:
                removed_count += 1
                continue

        cleaned_lines.append(line)

    cleaned_content = "".join(cleaned_lines)

    # Validate Python AST Syntax
    try:
        ast.parse(cleaned_content)
        syntax_status = "VALID"
    except SyntaxError as e:
        syntax_status = f"SYNTAX ERROR (Line {e.lineno}): {e.msg}"
        # Fallback safeguard: Keep basic structure if syntax fails
        cleaned_content = content

    # Write back cleaned version with a backup
    bak_path = filepath + '.master.bak'
    with open(bak_path, 'w', encoding='utf-8') as f:
        f.write(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"    -> Status: {syntax_status} | Removed Bloat Lines: {removed_count}")

def generate_unified_launcher():
    launcher_path = os.path.join(TARGET_DIR, "launch_cluster.py")
    launcher_code = '''#!/usr/bin/env python3
import subprocess
import time
import sys
import os

os.chdir("/home/joshua445/tollbridge_system")

services = [
    ("Simple Forwarder", ["python3", "simple_forwarder.py"]),
    ("Gateway Module", ["python3", "-m", "uvicorn", "gateway_module:app", "--host", "127.0.0.1", "--port", "8001"]),
    ("Master Cluster", ["python3", "master_cluster.py"])
]

print("=== INITIATING BARE-METAL TOLLBRIDGE CLUSTER ===")
processes = []

for name, cmd in services:
    print(f"[LAUNCHING] {name}...")
    p = subprocess.Popen(cmd)
    processes.append((name, p))
    time.sleep(1.5)

print("=== ALL SERVICES INITIALIZED. MONITORING STREAMS ===")
try:
    while True:
        time.sleep(5)
        for name, p in processes:
            if p.poll() is not None:
                print(f"[WARNING] {name} exited with code {p.returncode}. Restarting...")
                processes.remove((name, p))
                new_p = subprocess.Popen(cmd if name == "Master Cluster" else cmd) # restart mapping
                processes.append((name, new_p))
except KeyboardInterrupt:
    print("\\n[SHUTDOWN] Terminating cluster daemons...")
    for name, p in processes:
        p.terminate()
    print("Cluster stopped cleanly.")
'''
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    os.chmod(launcher_path, 0o755)
    print(f"[SUCCESS] Generated unified cluster launcher at {launcher_path}")

if __name__ == "__main__":
    print("=== STARTING SYSTEM-WIDE REPAIR & UNIFICATION ===")
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith('.py') and not file.startswith('master_architect') and not file.endswith('.bak'):
                audit_and_repair_file(os.path.join(root, file))
    
    generate_unified_launcher()
    print("=== SYSTEM OPTIMIZATION COMPLETE ===")
