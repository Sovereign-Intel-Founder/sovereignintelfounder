#!/usr/bin/env python3
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
    print("\n[SHUTDOWN] Terminating cluster daemons...")
    for name, p in processes:
        p.terminate()
    print("Cluster stopped cleanly.")
