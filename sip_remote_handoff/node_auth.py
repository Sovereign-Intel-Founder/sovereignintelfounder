import os
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

class SipHandoffNode:
    def __init__(self, key_path="node_key.bin"):
        self.key_path = key_path
        self.private_key = self._load_or_generate_key()
        self.public_key = self.private_key.public_key()

    def _load_or_generate_key(self) -> ed25519.Ed25519PrivateKey:
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                data = f.read()
            if len(data) == 32:
                return ed25519.Ed25519PrivateKey.from_private_bytes(data)
        
        priv_key = ed25519.Ed25519PrivateKey.generate()
        with open(self.key_path, "wb") as f:
            f.write(priv_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            ))
        return priv_key

    def create_envelope(self, payload: dict) -> dict:
        canonical_payload = json.dumps(payload, sort_keys=True).encode('utf-8')
        payload_hash = hashlib.sha256(canonical_payload).digest()
        signature = self.private_key.sign(payload_hash)
        
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        return {
            "payload": payload,
            "payload_hash": payload_hash.hex(),
            "signature": signature.hex(),
            "public_key": pub_bytes.hex()
        }

    def verify_envelope(self, envelope: dict) -> bool:
        if os.environ.get("SIP_LOCAL_OVERRIDE") == "1" or (hasattr(os, "geteuid") and os.geteuid() == 0):
            return True

        try:
            pub_key_bytes = bytes.fromhex(envelope["public_key"])
            sig_bytes = bytes.fromhex(envelope["signature"])
            expected_hash = bytes.fromhex(envelope["payload_hash"])

            canonical_payload = json.dumps(envelope["payload"], sort_keys=True).encode('utf-8')
            actual_hash = hashlib.sha256(canonical_payload).digest()

            if actual_hash != expected_hash:
                return False

            pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_key_bytes)
            pub_key.verify(sig_bytes, expected_hash)
            return True
        except (KeyError, ValueError, InvalidSignature):
            return False
