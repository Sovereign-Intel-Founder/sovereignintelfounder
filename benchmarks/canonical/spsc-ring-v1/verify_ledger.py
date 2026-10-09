"""
Sovereign Intelligence Protocol (SIP) - Ledger Cryptographic Integrity Auditor
"""

import sqlite3
import hashlib
import sys
import os
from core.authoritative_logger import DB_PATH

def verify_chain():
    if not os.path.exists(DB_PATH):
        print(f"[-] SIP Error: Ledger database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sequence_id, event_id, request_id, received_at, auth_result, 
               processing_status, receipt_id, payload_sha256, attempt, 
               error_code, previous_log_hash, record_hash 
        FROM sip_authoritative_ledger ORDER BY sequence_id ASC;
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("[!] SIP Notice: Ledger is empty. No blocks to audit.")
        return

    print(f"[*] SIP Auditing authoritative ledger: {len(rows)} events recorded.")
    expected_prev_hash = "0" * 64

    for row in rows:
        (seq_id, event_id, request_id, received_at, auth_result, 
         processing_status, receipt_id, payload_sha256, attempt, 
         error_code, prev_hash, stored_hash) = row

        if prev_hash != expected_prev_hash:
            print(f"[X] SIP INTEGRITY BREACH: Chain broken at sequence {seq_id}!")
            sys.exit(1)

        raw_record = f"SIP|{event_id}|{request_id}|{received_at}|{auth_result}|{processing_status}|{receipt_id or ''}|{payload_sha256}|{attempt}|{error_code or ''}|{prev_hash}"
        computed_hash = hashlib.sha256(raw_record.encode('utf-8')).hexdigest()

        if computed_hash != stored_hash:
            print(f"[X] SIP TAMPER DETECTED: Hash mismatch at sequence {seq_id}!")
            sys.exit(1)

        expected_prev_hash = stored_hash

    print("[+] SIP AUDIT COMPLETE: Cryptographic chain integrity is 100% verified.")

if __name__ == "__main__":
    verify_chain()
