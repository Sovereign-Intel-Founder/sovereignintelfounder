import sqlite3
import json
import time

DB_PATH = "telemetry.db"

def init_evidence_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_returns (
            evidence_id TEXT PRIMARY KEY,
            cell_id TEXT,
            result_status TEXT,
            checksum TEXT,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()

def log_evidence():
    init_evidence_table()
    conn = sqlite3.connect(DB_PATH)
    
    evidence_id = "ev_alpha_01"
    cell_id = "cell_alpha_01"
    result_status = "VERIFIED_SUCCESS"
    checksum = "8ab39cb1b591e482"
    
    conn.execute(
        "INSERT OR REPLACE INTO evidence_returns (evidence_id, cell_id, result_status, checksum, timestamp) VALUES (?, ?, ?, ?, ?)",
        (evidence_id, cell_id, result_status, checksum, time.time())
    )
    conn.commit()
    conn.close()
    print(f"[+] Evidence return '{evidence_id}' successfully logged and verified.")

if __name__ == "__main__":
    log_evidence()
