import json
import hashlib
from pydantic import BaseModel, Field, field_validator
from storage.db import get_db_connection

class IntelligenceObject(BaseModel):
    claim: str
    sources: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    jurisdiction: str = "global"
    lineage_hash: str | None = None
    signature: str | None = None

    @field_validator('sources')
    @classmethod
    def validate_sources(cls, v: list[str]) -> list[str]:
        if not v or not all(isinstance(s, str) and len(s) > 0 for s in v):
            raise ValueError("Intelligence object must contain a non-empty list of verifiable string sources.")
        return v

    def sign(self, secret_key: str = "sip_node_production_secret") -> None:
        """Cryptographically sign the payload and generate deterministic SHA-256 lineage hashes."""
        canonical_sources = json.dumps(sorted(self.sources), sort_keys=True)
        payload = f"{self.claim}|{canonical_sources}|{self.confidence}|{self.jurisdiction}"
        self.lineage_hash = hashlib.sha256((payload + secret_key).encode('utf-8')).hexdigest()
        self.signature = hashlib.sha256((self.lineage_hash + secret_key).encode('utf-8')).hexdigest()

    def commit(self) -> str:
        """Commit the signed intelligence object to the hardened SQLite WAL storage backend."""
        if not self.lineage_hash or not self.signature:
            self.sign()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO intelligence_objects 
                (lineage_hash, claim, sources, confidence, jurisdiction, signature)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.lineage_hash,
                self.claim,
                json.dumps(self.sources),
                self.confidence,
                self.jurisdiction,
                self.signature
            ))
        return self.lineage_hash
