import os
import json
import hashlib

def validate_state():
    print("[VALIDATOR] Starting Sovereign Seed Commons state validation...")
    
    # 1. Verify Identity
    if not os.path.exists("identity/identity.json") or not os.path.exists("identity/genesis.json"):
        raise FileNotFoundError("Identity files missing.")
    with open("identity/identity.json", "r") as f:
        identity = json.load(f)
    assert identity["name"] == "Sovereign Seed", "Invalid identity name."
    print("[OK] Identity files verified.")

    # 2. Verify Memory Schemas & Hashes
    if os.path.exists("memory/events.jsonl"):
        with open("memory/events.jsonl", "r") as f:
            for line in f:
                if not line.strip():
                    continue
                event = json.loads(line)
                assert "id" in event, "Event missing ID."
                assert "content_hash" in event, "Event missing content hash."
                computed_hash = hashlib.sha256(event["content"].encode("utf-8")).hexdigest()
                assert computed_hash == event["content_hash"], f"Content hash mismatch in event {event['id']}"
    print("[OK] Memory schemas and content hashes verified.")

    # 3. Verify Lineage
    if not os.path.exists("lineage/manifest.jsonl"):
        raise FileNotFoundError("Lineage manifest missing.")
    with open("lineage/manifest.jsonl", "r") as f:
        manifest = json.loads(f.readline())
    curr_gen = manifest["current_generation"]
    gen_file = f"lineage/generations/gen_{curr_gen}.json"
    if not os.path.exists(gen_file):
        raise FileNotFoundError(f"Generation file {gen_file} missing.")
    with open(gen_file, "r") as f:
        gen_data = json.load(f)
    assert gen_data["generation"] == curr_gen, "Generation mismatch."
    print(f"[OK] Lineage verified for Generation {curr_gen}.")

    print("[SUCCESS] All state validation checks passed successfully.")
    return True

if __name__ == "__main__":
    validate_state()
