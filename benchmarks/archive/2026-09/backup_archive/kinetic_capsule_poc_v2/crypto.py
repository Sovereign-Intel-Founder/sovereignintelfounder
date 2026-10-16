"""
Sovereign Intelligence Protocol - Kinetic Capsule PoC v2
Cryptographic Module (Ed25519 via PyNaCl & SHA-256 Commitments)
"""
import os
import json
import hashlib
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

DOMAIN_CHECKPOINT = b"SIP-KINETIC-CHECKPOINT-V2:"
DOMAIN_RECEIPT = b"SIP-KINETIC-RECEIPT-V2:"

def generate_keypair():
    """Generates a fresh Ed25519 signing key at runtime."""
    return SigningKey.generate()

def get_signing_key(key_path=".local_signing_key.hex"):
    """Loads a signing key from an ignored local file or generates and saves one."""
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as kf:
            secret_hex = kf.read().strip()
            return SigningKey(bytes.fromhex(secret_hex))
    sk = SigningKey.generate()
    with open(key_path, "w", encoding="utf-8") as kf:
        kf.write(sk.encode().hex())
    return sk

def canonicalize(payload: dict) -> bytes:
    """Deterministic JSON serialization excluding the signature field."""
    payload_copy = {k: v for k, v in payload.items() if k != "signature"}
    return json.dumps(payload_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def compute_hash(payload: dict) -> str:
    """Computes a standard SHA-256 hash of the canonicalized payload for commitments."""
    return hashlib.sha256(canonicalize(payload)).hexdigest()

def sign_payload(signing_key: SigningKey, payload: dict, is_receipt: bool = None) -> str:
    """Signs the canonical payload with automatic domain separation based on payload structure."""
    if is_receipt is None:
        is_receipt = "previous_receipt_hash" in payload
    prefix = DOMAIN_RECEIPT if is_receipt else DOMAIN_CHECKPOINT
    canonical_bytes = canonicalize(payload)
    signed_message = signing_key.sign(prefix + canonical_bytes)
    return signed_message.signature.hex()

def sign_artifact(payload: dict, is_receipt: bool = None, key_path=".local_signing_key.hex") -> str:
    """Convenience wrapper for cell callers passing only payload."""
    sk = get_signing_key(key_path)
    return sign_payload(sk, payload, is_receipt=is_receipt)

def verify_signature(payload: dict, is_receipt: bool = None, verify_key_hex: str = None) -> bool:
    """Verifies an Ed25519 signature against the canonical payload with automatic domain separation."""
    if not isinstance(payload, dict) or "signature" not in payload:
        return False
    if is_receipt is None:
        is_receipt = "previous_receipt_hash" in payload
    sig_hex = payload["signature"]
    prefix = DOMAIN_RECEIPT if is_receipt else DOMAIN_CHECKPOINT
    canonical_bytes = canonicalize(payload)
    try:
        if verify_key_hex:
            verify_key = VerifyKey(bytes.fromhex(verify_key_hex))
        else:
            verify_key = get_signing_key().verify_key
        verify_key.verify(prefix + canonical_bytes, bytes.fromhex(sig_hex))
        return True
    except (BadSignatureError, ValueError):
        return False
