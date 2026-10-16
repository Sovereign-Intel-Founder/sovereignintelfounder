import sys
import os
import json
from .crypto import compute_hash, verify_signature
from .capsule_core import CODE_COMMITMENT, INPUT_COMMITMENT, get_reference_result, execute_steps

CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "checkpoint_500.json")
RECEIPT_PATH = os.path.join(os.path.dirname(__file__), "final_receipt.json")

def verify_lineage():
    if not os.path.exists(CHECKPOINT_PATH) or not os.path.exists(RECEIPT_PATH):
        return False, "Missing checkpoint or receipt artifacts."
        
    with open(CHECKPOINT_PATH, "r") as f:
        cp = json.load(f)
    with open(RECEIPT_PATH, "r") as f:
        rc = json.load(f)
        
    if not verify_signature(cp):
        return False, "Checkpoint signature verification failed."
    if not verify_signature(rc):
        return False, "Receipt signature verification failed."
        
    expected_prev = compute_hash(cp)
    if rc.get("previous_receipt_hash") != expected_prev:
        return False, "Receipt predecessor link broken."
        
    if cp.get("sequence_number") != 500 or rc.get("sequence_number") != 1000:
        return False, "Sequence number continuity failed."
        
    ref = get_reference_result()
    if rc.get("final_state") != ref["final_state"] or rc.get("final_accumulator") != ref["accumulator"]:
        return False, "Migrated final result does not match uninterrupted reference result."
        
    return True, "Lineage and state verified successfully."

if __name__ == "__main__":
    success, msg = verify_lineage()
    if success:
        print(f"[Verifier] Passed: {msg}")
        sys.exit(0)
    else:
        print(f"[Verifier] Failed: {msg}")
        sys.exit(1)
