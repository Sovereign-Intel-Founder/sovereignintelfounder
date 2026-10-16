import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519

DOMAIN_LABEL = b"SIP-TRANSPORT-ENVELOPE-V1"

def canonical_json_bytes(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def compute_artifact_sha256(artifact: dict) -> str:
    canonical = canonical_json_bytes(artifact)
    return hashlib.sha256(canonical).hexdigest()

def sign_envelope_payload(payload: dict, private_key: ed25519.Ed25519PrivateKey) -> str:
    canonical = canonical_json_bytes(payload)
    signed_data = DOMAIN_LABEL + b":" + canonical
    sig_bytes = private_key.sign(signed_data)
    return sig_bytes.hex()

def verify_envelope_signature(payload: dict, signature_hex: str, public_key: ed25519.Ed25519PublicKey) -> bool:
    try:
        canonical = canonical_json_bytes(payload)
        signed_data = DOMAIN_LABEL + b":" + canonical
        sig_bytes = bytes.fromhex(signature_hex)
        public_key.verify(sig_bytes, signed_data)
        return True
    except Exception:
        return False
