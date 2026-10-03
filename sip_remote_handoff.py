import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class HandoffEnvelope:
    source_id: str
    timestamp: int
    payload: Dict[str, Any]
    signature: bytes

class RemoteHandoffIngestor:
    def __init__(self, shared_secret: bytes):
        """
        Initializes the remote handoff ingestion gate.
        shared_secret: Cryptographic anchor for validating incoming envelope signatures.
        """
        self.secret = shared_secret

    def process_envelope(self, raw_data: bytes) -> Optional[HandoffEnvelope]:
        """
        Parses and cryptographically verifies an incoming remote handoff envelope.
        Ensures tamper resistance and canonical structure before queue ingestion.
        """
        try:
            envelope_dict = json.loads(raw_data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

        source_id = envelope_dict.get("source_id")
        timestamp = envelope_dict.get("timestamp")
        payload = envelope_dict.get("payload")
        signature_hex = envelope_dict.get("signature")

        if not all([source_id, timestamp, payload, signature_hex]):
            return None

        try:
            signature = bytes.fromhex(signature_hex)
        except ValueError:
            return None

        # Reconstruct canonical payload for verification
        canonical_string = f"{source_id}:{timestamp}:{json.dumps(payload, sort_keys=True)}"
        expected_sig = hmac.new(self.secret, canonical_string.encode('utf-8'), hashlib.sha256).digest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        return HandoffEnvelope(
            source_id=source_id,
            timestamp=int(timestamp),
            payload=payload,
            signature=signature
        )
