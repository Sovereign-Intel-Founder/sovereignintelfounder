import sqlite3
import json
import time

DB_PATH = "telemetry.db"

def init_cell_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS protocol_cells (
            cell_id TEXT PRIMARY KEY,
            status TEXT,
            task_manifest TEXT,
            updated_at REAL
        )
    """)
    conn.commit()
    conn.close()

def register_and_run_cell():
    init_cell_table()
    conn = sqlite3.connect(DB_PATH)
    
    # Register a sample autonomous protocol cell manifest
    cell_id = "cell_alpha_01"
    manifest = json.dumps({"action": "mesh_index_sync", "priority": "high", "lanes": 128})
    
    conn.execute(
        "INSERT OR REPLACE INTO protocol_cells (cell_id, status, task_manifest, updated_at) VALUES (?, ?, ?, ?)",
        (cell_id, "EXECUTING", manifest, time.time())
    )
    conn.commit()
    conn.close()
    print(f"[+] Autonomous protocol cell '{cell_id}' registered and initialized in WAL persistence.")

if __name__ == "__main__":
    register_and_run_cell()
