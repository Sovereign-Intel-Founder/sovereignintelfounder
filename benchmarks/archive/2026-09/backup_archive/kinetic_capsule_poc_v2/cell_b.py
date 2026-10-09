import sys
import os
import time
import json
from .crypto import compute_hash, sign_artifact, verify_signature
from .capsule_core import CODE_COMMITMENT, INPUT_COMMITMENT, execute_steps

CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "checkpoint_500.json")
RECEIPT_PATH = os.path.join(os.path.dirname(__file__), "final_receipt.json")

REVOKED_CELLS = set()
USED_NONCES = set()

def validate_checkpoint(cp: dict) -> str:
    if cp.get("schema_version") != "2.0":
        return "REJECTED: unsupported schema version"
    if not verify_signature(cp):
        return "REJECTED: invalid signature"
    if cp.get("capsule_id") != "capsule-alpha-01":
        return "REJECTED: invalid capsule identity"
    if cp.get("code_commitment") != CODE_COMMITMENT:
        return "REJECTED: invalid code commitment"
    if cp.get("input_commitment") != INPUT_COMMITMENT:
        return "REJECTED: invalid input commitment"
    if cp.get("destination_cell") != "Cell-B" or cp.get("destination_cell") in REVOKED_CELLS:
        return "REJECTED: destination authorization failed or revoked"
    nonce = cp.get("nonce")
    if not nonce or nonce in USED_NONCES:
        return "REJECTED: nonce reuse or missing nonce"
    if cp.get("sequence_number") != 500:
        return "REJECTED: invalid sequence number"
    if not cp.get("previous_receipt_hash"):
        return "REJECTED: missing previous receipt hash"
    if cp.get("expiration", 0) < time.time():
        return "REJECTED: checkpoint expired"
    expected_state_hash = compute_hash({"state": cp.get("state"), "accumulator": cp.get("accumulator")})
    if cp.get("state_hash") != expected_state_hash:
        return "REJECTED: state hash mismatch"
    return "VALID"

def run_cell_b():
    print("[Cell B] Process started independently (PID: {})".format(os.getpid()))
    
    if not os.path.exists(CHECKPOINT_PATH):
        print("ERROR: Checkpoint file not found.")
        sys.exit(1)
        
    with open(CHECKPOINT_PATH, "r") as f:
        checkpoint = json.load(f)
        
    status = validate_checkpoint(checkpoint)
    if status != "VALID":
        print(f"[Cell B] Validation failed: {status}")
        sys.exit(1)
        
    print("[Cell B] Signature verified.")
    print("[Cell B] Destination verified.")
    
    USED_NONCES.add(checkpoint["nonce"])
    
    resuming_step = checkpoint["state_step"]
    print(f"[Cell B] Resumed at step {resuming_step}.")
    
    final_state, final_accumulator = execute_steps(
        resuming_step, 1000, 
        initial_state=checkpoint["state"], 
        initial_accumulator=checkpoint["accumulator"]
    )
    
    print("[Cell B] Completed at step 1,000.")
    
    receipt = {
        "schema_version": "2.0",
        "capsule_id": checkpoint["capsule_id"],
        "task_id": checkpoint["task_id"],
        "sequence_number": 1000,
        "previous_receipt_hash": compute_hash(checkpoint),
        "executing_cell": "Cell-B",
        "final_state": final_state,
        "final_accumulator": final_accumulator,
        "final_result": compute_hash({"state": final_state, "accumulator": final_accumulator}),
        "timestamp": time.time()
    }
    receipt["signature"] = sign_artifact(receipt)
    
    with open(RECEIPT_PATH, "w") as f:
        json.dump(receipt, f, indent=2)
        
    sys.exit(0)

if __name__ == "__main__":
    run_cell_b()
