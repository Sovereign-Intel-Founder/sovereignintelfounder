import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class IntelligenceObject:
    object_id: str
    source_id: str
    ingest_timestamp: int
    payload: Dict[str, Any]
    parent_hash: str
    provenance_hash: str

class ProvenanceStamper:
    def __init__(self, node_identity_key: str):
        """
        Initializes the provenance stamper for converting raw observations
        into immutable, cryptographically chained intelligence objects.
        """
        self.node_id = node_identity_key
        self.last_hash = hashlib.sha256(b"GENESIS_BLOCK_ROOT").hexdigest()

    def stamp_observation(self, source_id: str, payload: Dict[str, Any], timestamp: int) -> IntelligenceObject:
        """
        Wraps an inbound observation into a strict provenance-backed object,
        binding it to the cryptographic hash chain.
        """
        ingest_time = int(time.time())
        
        # Construct the canonical body to be hashed for absolute immutability
        body = {
            "source_id": source_id,
            "ingest_timestamp": ingest_time,
            "original_timestamp": timestamp,
            "payload": payload,
            "parent_hash": self.last_hash
        }
        
        canonical_json = json.dumps(body, sort_keys=True).encode('utf-8')
        provenance_hash = hashlib.sha256(canonical_json).hexdigest()
        
        # Generate a unique deterministic ID for the object
        object_id = hashlib.sha256(f"{source_id}:{provenance_hash}".encode('utf-8')).hexdigest()

        obj = IntelligenceObject(
            object_id=object_id,
            source_id=source_id,
            ingest_timestamp=ingest_time,
            payload=payload,
            parent_hash=self.last_hash,
            provenance_hash=provenance_hash
        )

        # Advance the chain's state pointer
        self.last_hash = provenance_hash
        return obj
