import sqlite3
import uuid
import os
from core.authoritative_logger import record_event, DB_PATH

def init_nonce_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS durable_nonces (
            nonce TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def check_and_store_nonce(nonce: str) -> bool:
    """Returns True if nonce is fresh and successfully stored. False if replayed."""
    init_nonce_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO durable_nonces (nonce, created_at) VALUES (?, datetime('now'));", (nonce,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()

def process_secure_ingress(request_id: str, nonce: str, auth_signature_valid: bool, payload: dict):
    event_id = f"evt_{uuid.uuid4().hex}"
    
    # 1. Enforce Authentication Check
    if not auth_signature_valid:
        record_event(
            event_id=event_id,
            request_id=request_id,
            auth_result="rejected",
            processing_status="unauthorized",
            receipt_id=None,
            payload=payload,
            error_code="ERR_INVALID_SIGNATURE"
        )
        raise PermissionError("Ingress rejected: Invalid cryptographic signature.")

    # 2. Enforce Durable Replay Protection
    if not check_and_store_nonce(nonce):
        record_event(
            event_id=event_id,
            request_id=request_id,
            auth_result="accepted_auth_replayed_nonce",
            processing_status="rejected_replay",
            receipt_id=None,
            payload=payload,
            error_code="ERR_REPLAY_DETECTED"
        )
        raise ValueError("Ingress rejected: Duplicate nonce detected (Replay attack prevented).")

    # 3. Issue Synchronous Durable Receipt & Record Event
    receipt_id = f"rcpt_{uuid.uuid4().hex}"
    record_hash = record_event(
        event_id=event_id,
        request_id=request_id,
        auth_result="accepted",
        processing_status="completed_durable",
        receipt_id=receipt_id,
        payload=payload
    )

    return {
        "status": "success",
        "request_id": request_id,
        "receipt_id": receipt_id,
        "record_hash": record_hash
    }
