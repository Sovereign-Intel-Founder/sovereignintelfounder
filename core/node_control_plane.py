import os
import json
import hashlib
from core.crypto.ed25519_verify import verify_canonical_signature

class NodeControlPlane:
    def __init__(self, ledger_path="core/data/node_control.db"):
        os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
        self.ledger_path = ledger_path

    def process_enrollment(self, payload: dict) -> dict:
        public_key = payload.get("public_key")
        signature = payload.get("signature")
        message_data = payload.get("message", {})
        
        # Canonicalize message bytes for verification
        message_bytes = json.dumps(message_data, sort_keys=True).encode()
        
        if not public_key or not signature or not verify_canonical_signature(public_key, signature, message_bytes):
            return {"status": "REJECTED", "reason": "Invalid or missing Ed25519 signature"}
            
        return {"status": "SUCCESS", "node_id": hashlib.sha256(bytes.fromhex(public_key)).hexdigest()[:16]}

    def process_heartbeat(self, payload: dict) -> dict:
        public_key = payload.get("public_key")
        signature = payload.get("signature")
        message_data = payload.get("message", {})
        
        message_bytes = json.dumps(message_data, sort_keys=True).encode()
        
        if not public_key or not signature or not verify_canonical_signature(public_key, signature, message_bytes):
            return {"status": "REJECTED", "reason": "Invalid or missing Ed25519 signature"}
            
        return {"status": "ACK", "sequence": message_data.get("sequence", 0)}
