import sys
import os
import time
import json
from .crypto import compute_hash, sign_artifact
from .capsule_core import CODE_COMMITMENT, INPUT_COMMITMENT, execute_steps

CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "checkpoint_500.json")

def run_cell_a():
    print("[Cell A] Process started (PID: {})".format(os.getpid()))
    
    start_step = 0
    checkpoint_step = 500
    
    state, accumulator = execute_steps(start_step, checkpoint_step)
    state_hash = compute_hash({"state": state, "accumulator": accumulator})
    
    checkpoint = {
        "schema_version": "2.0",
        "capsule_id": "capsule-alpha-01",
        "task_id": "task-sip-2026-v2",
        "sequence_number": 500,
        "previous_receipt_hash": compute_hash({"genesis": True}),
        "source_cell": "Cell-A",
        "destination_cell": "Cell-B",
        "code_commitment": CODE_COMMITMENT,
        "input_commitment": INPUT_COMMITMENT,
        "nonce": "nonce-xyz-789012",
        "expiration": int(time.time()) + 3600,
        "state_step": checkpoint_step,
        "state": state,
        "accumulator": accumulator,
        "state_hash": state_hash,
        "final_result": None
    }
    
    checkpoint["signature"] = sign_artifact(checkpoint)
    
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(checkpoint, f, indent=2)
        
    print("[Cell A] Checkpoint created at step 500.")
    print("[Cell A] Exiting intentionally after checkpoint.")
    sys.exit(0)

if __name__ == "__main__":
    run_cell_a()
