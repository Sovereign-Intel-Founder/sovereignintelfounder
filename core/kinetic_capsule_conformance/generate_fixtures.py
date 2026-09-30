import os
import json
import time
from nacl.signing import SigningKey

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def canonical_json(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def sha256_hash(data: dict) -> str:
    import hashlib
    return hashlib.sha256(canonical_json(data)).hexdigest()

def execute_steps(start_step: int, end_step: int, initial_state: int = 0, initial_accumulator: int = 0):
    state = initial_state
    accumulator = initial_accumulator
    for step in range(start_step, end_step):
        state = (state + step * 3 + 7) % 1_000_003
        accumulator += state
    return state, accumulator

def generate_all_fixtures():
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    
    # 1. Generate fresh Ed25519 keypair in memory
    sk = SigningKey.generate()
    vk = sk.verify_key
    public_key_hex = vk.encode().hex()
    
    with open(os.path.join(FIXTURES_DIR, "public_key.json"), "w") as f:
        json.dump({"public_key": public_key_hex, "algorithm": "Ed25519"}, f, indent=2)
        
    code_commitment = sha256_hash({"module": "sovereign_intelligence_protocol", "version": "conformance-2.0"})
    input_commitment = sha256_hash({"task": "conformance_workload", "start": 0, "end": 1000})
    
    manifest = {
        "schema_version": "2.0",
        "capsule_id": "capsule-conformance-01",
        "task_id": "task-sip-conf-2026",
        "code_commitment": code_commitment,
        "input_commitment": input_commitment
    }
    with open(os.path.join(FIXTURES_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        
    # 2. Execute steps 0 to 500 for checkpoint
    state_500, acc_500 = execute_steps(0, 500)
    state_hash_500 = sha256_hash({"state": state_500, "accumulator": acc_500})
    genesis_prev_hash = sha256_hash({"genesis": True})
    
    checkpoint = {
        "schema_version": "2.0",
        "capsule_id": manifest["capsule_id"],
        "task_id": manifest["task_id"],
        "sequence_number": 500,
        "previous_receipt_hash": genesis_prev_hash,
        "source_cell": "Cell-A",
        "destination_cell": "Cell-B",
        "code_commitment": code_commitment,
        "input_commitment": input_commitment,
        "nonce": "nonce-conf-123456",
        "expiration": int(time.time()) + 3600,
        "state_step": 500,
        "state": state_500,
        "accumulator": acc_500,
        "state_hash": state_hash_500
    }
    
    cp_bytes = canonical_json(checkpoint)
    checkpoint["signature"] = sk.sign(cp_bytes).signature.hex()
    
    with open(os.path.join(FIXTURES_DIR, "checkpoint.json"), "w") as f:
        json.dump(checkpoint, f, indent=2)
        
    # 3. Execute steps 500 to 1000 for final receipt
    state_1000, acc_1000 = execute_steps(500, 1000, initial_state=state_500, initial_accumulator=acc_500)
    
    receipt = {
        "schema_version": "2.0",
        "capsule_id": manifest["capsule_id"],
        "task_id": manifest["task_id"],
        "sequence_number": 1000,
        "previous_receipt_hash": sha256_hash(checkpoint),
        "executing_cell": "Cell-B",
        "final_state": state_1000,
        "final_accumulator": acc_1000,
        "final_result": sha256_hash({"state": state_1000, "accumulator": acc_1000}),
        "timestamp": int(time.time())
    }
    
    rc_bytes = canonical_json(receipt)
    receipt["signature"] = sk.sign(rc_bytes).signature.hex()
    
    receipts_doc = {"receipts": [receipt]}
    with open(os.path.join(FIXTURES_DIR, "receipts.json"), "w") as f:
        json.dump(receipts_doc, f, indent=2)
        
    final_state_doc = {
        "final_state": state_1000,
        "accumulator": acc_1000,
        "state_hash": sha256_hash({"state": state_1000, "accumulator": acc_1000})
    }
    with open(os.path.join(FIXTURES_DIR, "final_state.json"), "w") as f:
        json.dump(final_state_doc, f, indent=2)
        
    reference_state_doc = final_state_doc.copy()
    with open(os.path.join(FIXTURES_DIR, "reference_state.json"), "w") as f:
        json.dump(reference_state_doc, f, indent=2)
        
    # 4. Generate Adversarial Fixtures
    import copy
    
    def save_adv(name, mutator):
        adv = copy.deepcopy(checkpoint)
        mutator(adv)
        if name != "altered_signature":
            adv["signature"] = sk.sign(canonical_json({k: v for k, v in adv.items() if k != "signature"})).signature.hex()
        
        if name == "altered_signature":
            adv["signature"] = "deadbeef" * 8
        elif name == "expired":
            adv["expiration"] = 1000
        elif name == "altered_state":
            adv["state"] = 999999
        elif name == "altered_input":
            adv["input_commitment"] = "badinput" * 8
        elif name == "altered_destination":
            adv["destination_cell"] = "Cell-Z"
        elif name == "altered_sequence":
            adv["sequence_number"] = 499
        elif name == "altered_nonce":
            adv["nonce"] = ""
        elif name == "altered_prev_hash":
            adv["previous_receipt_hash"] = "00" * 32
            
        with open(os.path.join(FIXTURES_DIR, f"adv_{name}.json"), "w") as f:
            json.dump(adv, f, indent=2)

    save_adv("altered_state", lambda c: None)
    save_adv("altered_input", lambda c: None)
    save_adv("altered_destination", lambda c: None)
    save_adv("altered_sequence", lambda c: None)
    save_adv("altered_nonce", lambda c: None)
    save_adv("altered_prev_hash", lambda c: None)
    save_adv("altered_signature", lambda c: None)
    save_adv("expired", lambda c: None)
    
    print("[Fixture Generator] All valid and adversarial fixtures generated successfully.")

if __name__ == "__main__":
    generate_all_fixtures()
