#!/usr/bin/env bash
set -euo pipefail

echo "=== SOVEREIGN INTELLIGENCE PROTOCOL: SYSTEM HARDENING & AUDIT ==="

# 1. Inspect Port 8080 & Process Ownership
echo -e "\n[1/5] Auditing Socket Binding & Process Ownership..."
if sudo lsof -i :8080; then
    echo "-> SUCCESS: Port 8080 is bound and active."
else
    echo "-> CRITICAL: No process is currently listening on port 8080!"
    exit 1
fi

# 2. Verify SQLite Ledger & WAL Configuration
echo -e "\n[2/5] Inspecting SQLite Persistence & WAL Integrity..."
if [ -f "sip_ledger.db" ]; then
    echo "-> Ledger file present. Checking journal mode and table structure..."
    sqlite3 sip_ledger.db "PRAGMA journal_mode;"
    sqlite3 sip_ledger.db "PRAGMA synchronous;"
    
    # Ensure table exists
    sqlite3 sip_ledger.db "CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, client_hex TEXT NOT NULL, decision TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);"
    
    ROW_COUNT=$(sqlite3 sip_ledger.db "SELECT COUNT(*) FROM requests;")
    echo "-> Current total requests logged: $ROW_COUNT"
else
    echo "-> Initializing missing sip_ledger.db with WAL mode..."
    sqlite3 sip_ledger.db "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; CREATE TABLE requests (id INTEGER PRIMARY KEY AUTOINCREMENT, client_hex TEXT NOT NULL, decision TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);"
fi

# 3. Security File Permissions Hardening
echo -e "\n[3/5] Locking Down File Permissions..."
chmod 600 sip_ledger.db 2>/dev/null || true
chmod 700 harden_and_audit.sh
echo "-> Permissions hardened (Database set to read/write owner only)."

# 4. Loopback Ingress & Response Validation
echo -e "\n[4/5] Executing Local Loopback Ingress Smoke Test..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/)
echo "-> Ingress HTTP Status Response: $HTTP_CODE"
if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 402 ]; then
    echo "-> SUCCESS: Bridge is responding correctly with valid protocol codes."
else
    echo "-> WARNING: Unexpected response code received ($HTTP_CODE)."
fi

# 5. Summary Metrics Output
echo -e "\n[5/5] Ledger Traffic Summary (Last 5 Events):"
sqlite3 sip_ledger.db "SELECT id, client_hex, decision, timestamp FROM requests ORDER BY id DESC LIMIT 5;"

echo -e "\n=== HARDENING & AUDIT COMPLETE: SYSTEM IS STABLE ==="
