import json, hashlib
event = {
    "id": "sha256:" + hashlib.sha256(b"genesis-event-0").hexdigest(),
    "generation": 0,
    "type": "genesis_birth",
    "timestamp": "2026-09-22T11:00:00Z",
    "author": "Joshua Kleinsasser",
    "content_hash": hashlib.sha256(b"Sovereign Seed Commons Genesis Chamber initialized.").hexdigest(),
    "parent_references": [],
    "verification_state": "verified",
    "content": "Sovereign Seed Commons initialized in bare-metal Genesis Chamber."
}
with open("memory/events.jsonl", "w") as f:
    f.write(json.dumps(event) + "\n")
print("Memory restored.")
