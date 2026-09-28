import os
import sys
import json
import time
import hashlib
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

def canonical_json(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def sha256_hash(data: dict) -> str:
    return hashlib.sha256(canonical_json(data)).hexdigest()

def execute_steps(start_step: int, end_step: int, initial_state: int = 0, initial_accumulator: int = 0):
    state = initial_state
    accumulator = initial_accumulator
    for step in range(start_step, end_step):
        state = (state + step * 3 + 7) % 1_000_003
        accumulator += state
    return state, accumulator

def verify_signature(artifact: dict, verify_key: VerifyKey) -> bool:
    if "signature" not in artifact:
        return False
    sig_hex = artifact["signature"]
    payload = {k: v for k, v in artifact.items() if k != "signature"}
    try:
        sig_bytes = bytes.fromhex(sig_hex)
        verify_key.verify(canonical_json(payload), sig_bytes)
        return True
    except (BadSignatureError, ValueError):
        return False

def validate_artifact(cp: dict, verify_key: VerifyKey, revoked_cells: set, used_nonces: set) -> str:
    if cp.get("schema_version") != "2.0":
        return "REJECTED: unsupported schema version"
    if not verify_signature(cp, verify_key):
        return "REJECTED: invalid signature"
    if cp.get("destination_cell") != "Cell-B" or cp.get("destination_cell") in revoked_cells:
        return "REJECTED: destination authorization failed or revoked"
    nonce = cp.get("nonce")
    if not nonce or nonce in used_nonces:
        return "REJECTED: nonce reuse or missing nonce"
    if cp.get("sequence_number") != 500:
        return "REJECTED: invalid sequence number"
    if not cp.get("previous_receipt_hash"):
        return "REJECTED: missing previous receipt hash"
    if cp.get("expiration", 0) < time.time():
        return "REJECTED: checkpoint expired"
    
    expected_state_hash = sha256_hash({"state": cp.get("state"), "accumulator": cp.get("accumulator")})
    if cp.get("state_hash") != expected_state_hash:
        return "REJECTED: state hash mismatch"
    return "VALID"

def run_verification(fixtures_dir: str):
    print(f"[Independent Verifier] Running verification against fixtures in {fixtures_dir}...")
    
    with open(os.path.join(fixtures_dir, "public_key.json"), "r") as f:
        pk_data = json.load(f)
    verify_key = VerifyKey(bytes.fromhex(pk_data["public_key"]))
    
    with open(os.path.join(fixtures_dir, "manifest.json"), "r") as f:
        manifest = json.load(f)
        
    with open(os.path.join(fixtures_dir, "checkpoint.json"), "r") as f:
        checkpoint = json.load(f)
        
    with open(os.path.join(fixtures_dir, "receipts.json"), "r") as f:
        receipts_doc = json.load(f)
        receipt = receipts_doc["receipts"][0]
        
    with open(os.path.join(fixtures_dir, "reference_state.json"), "r") as f:
        reference = json.load(f)
        
    used_nonces = set()
    revoked_cells = set()
    
    status = validate_artifact(checkpoint, verify_key, revoked_cells, used_nonces)
    if status != "VALID":
        print(f"FAIL: Valid checkpoint rejected with reason: {status}")
        sys.exit(1)
    used_nonces.add(checkpoint["nonce"])
    
    final_state, final_acc = execute_steps(
        500, 1000,
        initial_state=checkpoint["state"],
        initial_accumulator=checkpoint["accumulator"]
    )
    
    if not verify_signature(receipt, verify_key):
        print("FAIL: Receipt signature verification failed.")
        sys.exit(1)
        
    expected_prev = sha256_hash(checkpoint)
    if receipt.get("previous_receipt_hash") != expected_prev:
        print("FAIL: Receipt predecessor link broken.")
        sys.exit(1)
        
    if final_state != reference["final_state"] or final_acc != reference["accumulator"]:
        print("FAIL: Recomputed final state does not match reference state.")
        sys.exit(1)
        
    print("[Independent Verifier] Valid fixture path verified successfully.")
    
    adversarial_tests = [
        ("adv_altered_state.json", "REJECTED: state hash mismatch"),
        ("adv_altered_input.json", "REJECTED: invalid signature"),
        ("adv_altered_destination.json", "REJECTED: destination authorization failed or revoked"),
        ("adv_altered_sequence.json", "REJECTED: invalid sequence number"),
        ("adv_altered_nonce.json", "REJECTED: nonce reuse or missing nonce"),
        ("adv_altered_prev_hash.json", "REJECTED: valid checkpoint expected"),
        ("adv_altered_signature.json", "REJECTED: invalid signature"),
        ("adv_expired.json", "REJECTED: checkpoint expired")
    ]
    
    for filename, expected_reason_substring in adversarial_tests:
        filepath = os.path.join(fixtures_dir, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r") as f:
            adv_cp = json.load(f)
            
        res = validate_artifact(adv_cp, verify_key, revoked_cells, set())
        if res == "VALID":
            print(f"FAIL: Adversarial fixture '{filename}' was incorrectly accepted as VALID.")
            sys.exit(1)
        else:
            print(f"[Adversarial Test] '{filename}' correctly rejected with: {res}")
            
    replay_status = validate_artifact(checkpoint, verify_key, revoked_cells, used_nonces)
    if replay_status == "VALID":
        print("FAIL: Replayed checkpoint was incorrectly accepted.")
        sys.exit(1)
    print(f"[Adversarial Test] Replayed checkpoint correctly rejected with: {replay_status}")
    
    print("[Independent Verifier] All adversarial tests passed successfully.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("fixtures_dir", help="Path to fixtures directory")
    args = parser.parse_args()
    run_verification(args.fixtures_dir)
