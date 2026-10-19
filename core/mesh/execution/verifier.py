"""
Sovereign Intelligence Protocol - Execution & Result Verification
Validates cryptographic evidence returns from worker nodes to ensure
tamper-evident task completion before credit assignment.
"""

from typing import Dict, Any
from dataclasses import dataclass
import hashlib
import json

@dataclass
class EvidenceReturn:
    task_id: str
    participant_id: str
    result_data: Dict[str, Any]
    output_hash: str
    signature: str

    def verify_integrity(self) -> bool:
        """
        Cryptographically verifies that the result data matches 
        the claimed output hash using canonical JSON serialization.
        """
        canonical_payload = json.dumps(self.result_data, sort_keys=True, separators=(',', ':'))
        computed_hash = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()
        return computed_hash == self.output_hash
