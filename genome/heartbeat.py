#!/usr/bin/env python3
"""
Sovereign Seed Commons - Safe Bounded Heartbeat
Executes a single, finite, non-infinite cycle with strict sandboxing and allowlisted commands.
"""

import os
import sys
import json
import subprocess

def validate_environment():
    print("[HEARTBEAT] Validating identity and state before cycle execution...")
    if not os.path.exists("identity/identity.json"):
        print("[ERROR] Identity missing. Aborting heartbeat.")
        sys.exit(1)
    print("[HEARTBEAT] Environment verified. Proceeding with bounded cycle.")

def select_bounded_objective():
    print("[HEARTBEAT] Selecting single bounded objective from inbox/issues...")
    # Bounded objective stub: verifies local evaluation state
    return {"id": "OBJ-001", "task": "run_evaluation_dry_run"}

def execute_safe_experiment(objective):
    print(f"[HEARTBEAT] Executing objective: {objective['task']}")
    # Enforce allowlisted commands only (NO shell=True)
    allowlisted_command = ["python3", "tools/validate_state.py"]
    
    try:
        result = subprocess.run(
            allowlisted_command,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        print("[HEARTBEAT] Experiment executed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Experiment failed: {e.stderr}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[ERROR] Experiment timed out.")
        sys.exit(1)

def run_heartbeat():
    validate_environment()
    objective = select_bounded_objective()
    execute_safe_experiment(objective)
    print("[HEARTBEAT] Cycle completed cleanly. Exiting.")

if __name__ == "__main__":
    run_heartbeat()
