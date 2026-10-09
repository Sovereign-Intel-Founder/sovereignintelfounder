"""
Sovereign Intelligence Protocol (SIP) - Authoritative Ledger Core
Provides cryptographic hash-chained, SQLite WAL-backed durable event logging.
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime, timezone

DB_PATH = os.getenv("SIP_LEDGER_PATH", "sovereign_intelligence_protocol.db")

def init_ledger():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sip_authoritative_ledger (
            sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE NOT NULL,
            request_id TEXT NOT NULL,
            received_at TEXT NOT NULL,
            auth_result TEXT NOT NULL,
            processing_status TEXT NOT NULL,
            receipt_id TEXT,
            payload_sha256 TEXT NOT NULL,
            attempt INTEGER NOT NULL,
            error_code TEXT,
            previous_log_hash TEXT NOT NULL,
            record_hash TEXT NOT NULL,
            protocol_tag TEXT DEFAULT 'SIP-v1'
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sip_durable_nonces (
            nonce TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def get_last_hash():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT record_hash FROM sip_authoritative_ledger ORDER BY sequence_id DESC LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "0" * 64

def record_event(event_id, request_id, auth_result, processing_status, receipt_id, payload, attempt=1, error_code=None):
    init_ledger()
    received_at = datetime.now(timezone.utc).isoformat()
    payload_str = json.dumps(payload, sort_keys=True)
    payload_sha256 = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    
    prev_hash = get_last_hash()
    
    raw_record = f"SIP|{event_id}|{request_id}|{received_at}|{auth_result}|{processing_status}|{receipt_id or ''}|{payload_sha256}|{attempt}|{error_code or ''}|{prev_hash}"
    record_hash = hashlib.sha256(raw_record.encode('utf-8')).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA synchronous=FULL;")
        conn.execute("""
            INSERT INTO sip_authoritative_ledger (
                event_id, request_id, received_at, auth_result, processing_status,
                receipt_id, payload_sha256, attempt, error_code, previous_log_hash, record_hash, protocol_tag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SIP-v1');
        """, (
            event_id, request_id, received_at, auth_result, processing_status,
            receipt_id, payload_sha256, attempt, error_code, prev_hash, record_hash
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"SIP Critical: Durable ledger write failed -> {e}")
    finally:
        conn.close()
        
    return record_hash
