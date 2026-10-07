import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("SIP_DB_PATH", "sovereign_intel.db")

@contextmanager
def get_db_connection():
    """Context manager enforcing WAL mode, optimized page caches, and native busy-timeout retry handling."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-64000;") # 64MB page cache allocation
    conn.execute("PRAGMA busy_timeout=5000;")  # Automatically retry busy locks for up to 5000ms
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Database transaction failed and was rolled back: {e}") from e
    finally:
        conn.close()

def init_db():
    """Initialize the intelligence schema, compound indexes, and dynamic compute-metering ledgers."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_objects (
                lineage_hash TEXT PRIMARY KEY,
                claim TEXT NOT NULL,
                sources TEXT NOT NULL,
                confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
                jurisdiction TEXT NOT NULL,
                signature TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jurisdiction_confidence 
            ON intelligence_objects(jurisdiction, confidence DESC);
        """)
        # Compute metering & bot account ledger
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_accounts (
                client_id TEXT PRIMARY KEY,
                credit_balance REAL NOT NULL DEFAULT 0.0,
                tier TEXT NOT NULL DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compute_ledger_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                compute_units INTEGER NOT NULL,
                query_type TEXT NOT NULL,
                charged_amount REAL NOT NULL,
                waived BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Insert a default test bot account with starter credits
        conn.execute("""
            INSERT OR IGNORE INTO bot_accounts (client_id, credit_balance, tier)
            VALUES ('test_trading_bot_alpha', 1000.0, 'standard_bot');
        """)
    print("[INFO] Sovereign Intelligence SQLite WAL storage and compute ledgers initialized.")

if __name__ == "__main__":
    init_db()
