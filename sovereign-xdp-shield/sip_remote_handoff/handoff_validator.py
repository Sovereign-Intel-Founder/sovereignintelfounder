#!/usr/bin/env python3
import hashlib
import json
import sys

def generate_envelope(node_id, payload, secret_key):
    canonical_data = json.dumps({"node_id": node_id, "payload": payload}, sort_keys=True)
    signature = hashlib.sha256((canonical_data + secret_key).encode('utf-8')).hexdigest()
    return {"envelope": canonical_data, "signature": signature}

def verify_envelope(envelope_json, signature, secret_key):
    expected_sig = hashlib.sha256((envelope_json + secret_key).encode('utf-8')).hexdigest()
    return expected_sig == signature

if __name__ == "__main__":
    secret = "sovereign_ashburn_anchor_2026"
    test_payload = {"status": "active", "metrics": {"cpu_load": 0.12, "ring_buffer": "healthy"}}
    
    env = generate_envelope("ashburn-core-01", test_payload, secret)
    print(f"[*] Generated SHA-256 Canonical Envelope...")
    
    is_valid = verify_verify = verify_envelope(env["envelope"], env["signature"], secret)
    if is_valid:
        print("[✓] Cryptographic Handoff Signature Verified: [PASSED]")
    else:
        print("[x] Cryptographic Handoff Signature Rejected: [FAILED]")
        sys.exit(1)
