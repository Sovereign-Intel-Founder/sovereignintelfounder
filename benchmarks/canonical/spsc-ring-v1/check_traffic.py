import sqlite3
import os

db_path = "core/sip_ledger.db" # Check standard paths if nested differently

# Find the database file dynamically if needed
if not os.path.exists(db_path):
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".db"):
                db_path = os.path.join(root, file)
                break

print(inspect_path := f"[*] Inspecting database at: {db_path}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check table schema first
    cur.execute("PRAGMA table_info(sip_authoritative_ledger);")
    columns = [col[1] for col in cur.fetchall()]
    print(f"[+] Ledger columns: {columns}")
    
    # Query distinct user_ids and actor_roles to see who has interacted
    cur.execute("SELECT DISTINCT user_id, actor_role, count(*) FROM sip_authoritative_ledger GROUP BY user_id, actor_role;")
    rows = cur.fetchall()
    
    print("\n[+] Recorded Interaction Summary:")
    if rows:
        for row in rows:
            print(f"    - User ID: {row[0]} | Role: {row[1]} | Event Count: {row[2]}")
    else:
        print("    [-] Ledger contains zero recorded events.")
        
    conn.close()
else:
    print("[-] No SQLite ledger database found in the workspace.")
