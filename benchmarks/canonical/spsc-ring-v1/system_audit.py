import os
import sqlite3
import json
import urllib.request
import subprocess

print("========================================")
print("     SIP SYSTEM DIAGNOSTIC AUDIT        ")
print("========================================")

# 1. Check Git Status & Branch
print("\n[+] 1. Git Repository State:")
git_status = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
print(git_status.stdout.strip())

# 2. Check Database & Ledger State
db_path = "core/sip_ledger.db" # Adjust if path differs
print(f"\n[+] 2. Authoritative Ledger Check ({db_path}):")
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        print(f"    Tables found: {tables}")
        if "sip_authoritative_ledger" in tables:
            cur.execute("SELECT COUNT(*), max(sequence_id) FROM sip_authoritative_ledger;")
            count, max_seq = cur.fetchone()
            print(f"    Total Events Committed: {count}")
            print(f"    Latest Sequence ID: {max_seq}")
        conn.close()
    except Exception as e:
        print(f"    Database read error: {e}")
else:
    print("    [-] Database file not found at expected path.")

# 3. Check Local Port Binding / Ingress Service
print("\n[+] 3. Ingress Service Local Probe:")
try:
    req = urllib.request.Request("http://127.0.0.1:8080/v1/audit")
    with urllib.request.urlopen(req, timeout=2) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"    Ingress Bridge Response: {data}")
except Exception as e:
    print(f"    [-] Ingress bridge is NOT responding on port 8080: {e}")

print("\n========================================")
print("       AUDIT COMPLETE                   ")
print("========================================")
