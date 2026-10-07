import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.exceptions import InvalidSignature

def verify_canonical_signature(public_key_hex: str, signature_b64: str, message_bytes: bytes) -> bool:
    try:
        pub_key_bytes = bytes.fromhex(public_key_hex)
        sig_bytes = base64.b64decode(signature_b64)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_key_bytes)
        public_key.verify(sig_bytes, message_bytes)
        return True
    except (ValueError, InvalidSignature, KeyError):
        return False
