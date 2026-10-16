#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sqlite3
import time
from pathlib import Path

FREE_USES = 8
FEE_SOL = "0.0001"


class QuotaGate:
    def __init__(self, db_path: str | Path, free_uses: int = FREE_USES) -> None:
        self.db_path = str(db_path)
        self.free_uses = free_uses
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None, check_same_thread=False)
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tollbridge_quota_clients (
                    client_hash TEXT PRIMARY KEY,
                    uses INTEGER NOT NULL DEFAULT 0 CHECK (uses >= 0),
                    first_seen REAL NOT NULL,
                    last_seen REAL NOT NULL
                )
            """)
        finally:
            conn.close()

    @staticmethod
    def client_hash(identifier: str) -> str:
        return hashlib.sha256(identifier.encode("utf-8")).hexdigest()

    def reserve(self, identifier: str) -> tuple[bool, int]:
        client_hash = self.client_hash(identifier)
        now = time.time()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT uses FROM tollbridge_quota_clients WHERE client_hash=?", (client_hash,)).fetchone()
            uses = int(row[0]) if row else 0
            if row is None:
                conn.execute("INSERT INTO tollbridge_quota_clients(client_hash, uses, first_seen, last_seen) VALUES(?,?,?,?)", (client_hash, 1, now, now))
                conn.execute("COMMIT")
                return True, 1
            if uses < self.free_uses:
                uses += 1
                conn.execute("UPDATE tollbridge_quota_clients SET uses=?, last_seen=? WHERE client_hash=?", (uses, now, client_hash))
                conn.execute("COMMIT")
                return True, uses
            conn.execute("UPDATE tollbridge_quota_clients SET last_seen=? WHERE client_hash=?", (now, client_hash))
            conn.execute("COMMIT")
            return False, uses
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def challenge(self, uses: int) -> dict[str, object]:
        return {
            "status": "payment_required",
            "error": "freemium_quota_exhausted",
            "free_uses": self.free_uses,
            "uses_recorded": uses,
            "micro_fee": {"amount": FEE_SOL, "currency": "SOL", "unit": "per_request"},
            "instructions": "Provide verifiable payment proof for the fixed 0.0001 SOL per-request fee before resubmitting.",
            "queue_inserted": False,
        }
