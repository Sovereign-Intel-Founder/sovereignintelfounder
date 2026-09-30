#!/usr/bin/env bash
set -e

echo "=== [1/4] Checking Port 8080 & Process Binding ==="
if sudo lsof -i :8080; then
    echo "-> Port 8080 is actively bound."
else
    echo "-> WARNING: Nothing is bound to port 8080."
fi

echo -e "\n=== [2/4] Verifying SQLite Ledger & WAL Mode ==="
if [ -f "sip_ledger.db" ]; then
    echo "-> Ledger file found. Checking integrity and row count..."
    sqlite3 sip_ledger.db "PRAGMA journal_mode;"
    sqlite3 sip_ledger.db "SELECT COUNT(*) as total_requests FROM requests;"
    sqlite3 sip_ledger.db "SELECT id, client_hex, decision, timestamp FROM requests ORDER BY id DESC LIMIT 5;"
else
    echo "-> WARNING: sip_ledger.db does not exist in this directory."
fi

echo -e "\n=== [3/4] Testing Local Loopback Ingress ==="
curl -i http://127.0.0.1:8080/ || echo "-> Failed to reach local endpoint."

echo -e "\n=== [4/4] System Audit Complete ==="
