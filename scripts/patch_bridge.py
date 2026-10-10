import glob

matches = glob.glob("**/toll_bridge*.py", recursive=True) + glob.glob("**/bridge*.py", recursive=True)
target_file = None

for m in matches:
    if "archive" not in m and "backup" not in m:
        target_file = m
        break

if target_file:
    with open(target_file, "r") as f:
        content = f.read()

    if "telemetry.db" not in content:
        # Add sqlite3 import and DB initialization snippet
        import_snippet = "import sqlite3\nimport time\n"
        
        wal_logic = """
def _persist_telemetry_payload(payload_bytes):
    try:
        conn = sqlite3.connect("telemetry.db")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("CREATE TABLE IF NOT EXISTS ingress_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, payload TEXT)")
        conn.execute("INSERT INTO ingress_logs (timestamp, payload) VALUES (?, ?)", (time.time(), payload_bytes))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"WAL persistence error: {e}")
"""
        
        new_content = import_snippet + wal_logic + "\n" + content
        with open(target_file, "w") as f:
            f.write(new_content)
        print(f"Successfully injected WAL persistence into {target_file}")
    else:
        print("WAL persistence code already exists in target.")
