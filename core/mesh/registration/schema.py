"""
Sovereign Intelligence Protocol - Participant Registration Schema
Defines cryptographic identity binding, capability advertisements, and 
durable participant admission contracts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import json
import hashlib
import re

class RegistrationValidationError(ValueError):
    """Raised when participant payload violates cryptographic or structural invariants."""
    pass


@dataclass
class ParticipantRegistration:
    participant_id: str
    public_key_pem: str
    supported_caps: List[str]
    endpoint_uri: str
    nonce: int
    signature: str
    registered_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.validate_structure()

    def validate_structure(self) -> None:
        """Enforces rigorous structural and format constraints."""
        if not self.participant_id or not isinstance(self.participant_id, str):
            raise RegistrationValidationError("Invalid or missing participant_id.")
        
        # Enforce UUIDv4 or strict alphanumeric cryptographic identifier format
        if not re.match(r"^[a-zA-Z0-9_\-\.]{3,128}$", self.participant_id):
            raise RegistrationValidationError(
                f"Participant ID '{self.participant_id}' fails strict format invariants."
            )

        if not self.public_key_pem or "BEGIN PUBLIC KEY" not in self.public_key_pem:
            raise RegistrationValidationError("Invalid public key material; PEM format required.")

        if not self.supported_caps or not isinstance(self.supported_caps, list):
            raise RegistrationValidationError("At least one capability descriptor must be declared.")

        for cap in self.supported_caps:
            if not isinstance(cap, str) or len(cap.strip()) == 0:
                raise RegistrationValidationError(f"Malformed capability identifier: {cap}")

        if not self.endpoint_uri or not (
            self.endpoint_uri.startswith("grpc://") or self.endpoint_uri.startswith("tcp://")
        ):
            raise RegistrationValidationError(
                f"Endpoint URI '{self.endpoint_uri}' must adhere to explicit transport schemes (grpc://, tcp://)."
            )

        if not isinstance(self.nonce, int) or self.nonce < 0:
            raise RegistrationValidationError("Nonce must be a non-negative integer.")

        if not self.signature or len(self.signature) < 64:
            raise RegistrationValidationError("Cryptographic signature payload missing or truncated.")

    def canonical_bytes(self) -> bytes:
        """
        Produces a deterministic, sorted JSON byte representation 
        for cryptographic verification and signing wrappers.
        """
        payload = {
            "participant_id": self.participant_id,
            "public_key_pem": self.public_key_pem.strip(),
            "supported_caps": sorted(self.supported_caps),
            "endpoint_uri": self.endpoint_uri,
            "nonce": self.nonce
        }
        return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')

    def compute_fingerprint(self) -> str:
        """Computes SHA-256 fingerprint of the canonical registration payload."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
