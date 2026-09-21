#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

HOST = os.environ.get("SIP_GATEWAY_HOST", "127.0.0.1")
PORT = int(os.environ.get("SIP_GATEWAY_PORT", "4021"))
DB_PATH = Path(os.environ.get("SIP_GATEWAY_DB", "/opt/tollbridge_system/tollbridge.db"))
UPSTREAM_DB = Path(os.environ.get("SIP_GATEWAY_CORE_DB", "/var/lib/tollbridge-core/toll_bridge.db"))

INGRESS_TOKEN = os.environ.get("SIP_GATEWAY_INGRESS_TOKEN", "")
FREE_USES = 8
FEE_SOL = "0.0001"
MAX_BODY_BYTES = 1_048_576

app = FastAPI(title="Tollbridge SIP Quota Gateway", version="1.0.0")


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _db()
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sip_quota_clients (
                client_hash TEXT PRIMARY KEY,
                uses INTEGER NOT NULL DEFAULT 0 CHECK (uses >= 0),
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sip_gateway_events (
                event_id TEXT PRIMARY KEY,
                client_hash TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sip_events_client ON sip_gateway_events(client_hash)")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_events (
                event_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_digest TEXT NOT NULL,
                stream_id TEXT,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                chain_status TEXT,
                chain_tx_hash TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pipeline_events_status ON pipeline_events(status, updated_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pipeline_events_digest ON pipeline_events(payload_digest)")
    finally:
        conn.close()


def _client_hash(identifier: str) -> str:
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def _take_free_use(client_hash: str) -> tuple[bool, int]:
    now = time.time()
    conn = _db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT uses FROM sip_quota_clients WHERE client_hash = ?", (client_hash,)).fetchone()
        uses = int(row["uses"]) if row else 0
        if row is None:
            conn.execute(
                "INSERT INTO sip_quota_clients(client_hash, uses, first_seen, last_seen) VALUES (?, 1, ?, ?)",
                (client_hash, now, now),
            )
            conn.execute("COMMIT")
            return True, 1
        if uses < FREE_USES:
            new_uses = uses + 1
            conn.execute("UPDATE sip_quota_clients SET uses = ?, last_seen = ? WHERE client_hash = ?", (new_uses, now, client_hash))
            conn.execute("COMMIT")
            return True, new_uses
        conn.execute("UPDATE sip_quota_clients SET last_seen = ? WHERE client_hash = ?", (now, client_hash))
        conn.execute("COMMIT")
        return False, uses
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def _record_event(event_id: str, client_hash: str, source: str, status: str) -> None:
    conn = _db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO sip_gateway_events(event_id, client_hash, source, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (event_id, client_hash, source, status, time.time()),
        )
    finally:
        conn.close()


def _valid_ingress_token(value: str | None) -> bool:
    if not INGRESS_TOKEN:
        return True
    return bool(value) and hmac.compare_digest(value, INGRESS_TOKEN)


@app.on_event("startup")
async def startup() -> None:
    init_db()


@app.get("/health")
async def health() -> dict[str, Any]:
    conn = _db()
    try:
        clients = conn.execute("SELECT COUNT(*) AS n FROM sip_quota_clients").fetchone()["n"]
        events = conn.execute("SELECT COUNT(*) AS n FROM sip_gateway_events").fetchone()["n"]
        return {
            "status": "operational",
            "service": "sip-quota-gateway",
            "port": PORT,
            "database": str(DB_PATH),
            "core_database": str(UPSTREAM_DB),
            "journal_mode": conn.execute("PRAGMA journal_mode").fetchone()[0],
            "financial_broadcast_enabled": False,
            "tracked_clients": clients,
            "recorded_events": events,
        }
    finally:
        conn.close()


@app.post("/v1/sip/ingest")
async def ingest(request: Request, x_client_token: str | None = Header(default=None), x_client_signature: str | None = Header(default=None), x_ingress_token: str | None = Header(default=None)) -> JSONResponse:
    if not _valid_ingress_token(x_ingress_token):
        raise HTTPException(status_code=401, detail="invalid ingress token")
    if request.headers.get("content-length") and int(request.headers["content-length"]) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="payload too large")
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="payload too large")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"invalid_json: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="payload must be a JSON object")
    identifier = x_client_token or x_client_signature
    if not identifier:
        raise HTTPException(status_code=400, detail="X-Client-Token or X-Client-Signature is required")
    client_hash = _client_hash(identifier)
    allowed, uses = await asyncio.to_thread(_take_free_use, client_hash)
    if not allowed:
        return JSONResponse(
            status_code=402,
            content={
                "status": "payment_required",
                "error": "freemium_quota_exhausted",
                "free_uses": FREE_USES,
                "uses_recorded": uses,
                "micro_fee": {"amount": FEE_SOL, "currency": "SOL", "unit": "per_request"},
                "instructions": "Provide verifiable payment proof for the fixed 0.0001 SOL per-request fee before resubmitting.",
                "queue_inserted": False,
            },
            headers={"X-Freemium-Quota": str(FREE_USES), "X-Quota-Uses": str(uses), "X-Payment-Required": FEE_SOL + " SOL"},
        )
    event_id = str(payload.get("event_id") or hashlib.sha256(raw + str(time.time_ns()).encode()).hexdigest())
    source = str(payload.get("source") or "sip-live")[:128]
    upstream_payload = {"operation": "sip_ingest", "event_id": event_id, "source": source, "payload": payload}
    try:
        inserted = await asyncio.to_thread(_forward, upstream_payload)
        _record_event(event_id, client_hash, source, "queued" if inserted else "duplicate")
    except Exception as exc:
        _record_event(event_id, client_hash, source, "upstream_error")
        raise HTTPException(status_code=503, detail="upstream raw-ingest unavailable") from exc
    return JSONResponse(status_code=202, content={"status": "accepted", "event_id": event_id, "free_use": uses, "remaining_free_uses": FREE_USES - uses, "queue_inserted": inserted})


def _forward(payload: dict[str, Any]) -> bool:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    event_id = str(payload["event_id"])
    source = str(payload.get("source") or "sip-live")[:128]
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    conn = sqlite3.connect(UPSTREAM_DB, timeout=30.0, isolation_level=None, check_same_thread=False)
    try:
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute(
            "INSERT OR IGNORE INTO pipeline_events(event_id, source, payload_json, payload_digest, status) VALUES (?, ?, ?, ?, 'queued')",
            (event_id, source, canonical, digest),
        )
        conn.execute("COMMIT")
        return cur.rowcount == 1
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sip_quota_gateway:app", host=HOST, port=PORT, loop="uvloop", http="httptools", workers=1)

__all__ = ["app"]

