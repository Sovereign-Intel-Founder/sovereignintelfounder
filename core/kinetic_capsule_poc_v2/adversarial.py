import sys
import os
import json
import copy
from .crypto import compute_hash, sign_artifact
from .cell_b import validate_checkpoint

def run_adversarial_suite():
    print("[Adversarial] Running mutation matrix and negative tests...")
    
    with open(os.path.join(os.path.dirname(__file__), "checkpoint_500.json"), "r") as f:
        base_cp = json.load(f)
        
    mutations = [
        ("state_hash", lambda c: c.update({"state_hash": "deadbeef" * 8})),
        ("state_payload", lambda c: c.update({"state": 999999})),
        ("input_commitment", lambda c: c.update({"input_commitment": "badinput" * 8})),
        ("code_commitment", lambda c: c.update({"code_commitment": "badcode" * 8})),
        ("destination_cell", lambda c: c.update({"destination_cell": "Cell-Z"})),
        ("capsule_id", lambda c: c.update({"capsule_id": "fake-capsule"})),
        ("task_id", lambda c: c.update({"task_id": "fake-task"})),
        ("sequence_number", lambda c: c.update({"sequence_number": 499})),
        ("nonce", lambda c: c.update({"nonce": "used-nonce-abc"})),
        ("previous_receipt_hash", lambda c: c.update({"previous_receipt_hash": "00" * 32})),
        ("expiration", lambda c: c.update({"expiration": 1000})),
        ("signature", lambda c: c.update({"signature": "badf00d" * 8})),
        ("schema_version", lambda c: c.update({"schema_version": "1.0"})),
        ("accumulator", lambda c: c.update({"accumulator": 12345}))
    ]
    
    for name, mutator in mutations:
        cp_copy = copy.deepcopy(base_cp)
        if name != "signature":
            cp_copy["signature"] = sign_artifact(cp_copy)
        mutator(cp_copy)
        
        status = validate_checkpoint(cp_copy)
        if status == "VALID":
            print(f"FAIL: Mutation '{name}' was incorrectly accepted as VALID.")
            sys.exit(1)
            
    print("[Adversarial] All 14 mutation tests rejected successfully.")
    
    cp_replay = copy.deepcopy(base_cp)
    from .cell_b import USED_NONCES
    USED_NONCES.add(cp_replay["nonce"])
    if validate_checkpoint(cp_replay) == "VALID":
        print("FAIL: Replay test accepted already used nonce.")
        sys.exit(1)
    print("[Adversarial] Replay test rejected successfully.")

    print("[Adversarial] Adversarial matrix passed.")

if __name__ == "__main__":
    run_adversarial_suite()
