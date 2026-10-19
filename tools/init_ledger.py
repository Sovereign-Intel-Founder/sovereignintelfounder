import os
import sqlite3
from pathlib import Path

def init_ledger():
    ledger_dir = Path("data")
    ledger_dir.mkdir(parents=True, exist_ok=True)
    db_path = ledger_dir / "sip_ledger.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create baseline ledger schema aligned with SIP telemetry and proof verification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            node_id TEXT,
            slot INTEGER,
            proof_hash TEXT,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[+] Ledger database successfully initialized at: {db_path}")

if __name__ == "__main__":
    init_ledger()
