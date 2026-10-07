set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "Removing local databases, logs, and caches..."
find "$SIP" \( -name "*.db" -o -name "*.db-wal" -o -name "*.db-shm" -o -name "*.log" -o -name "*.jsonl" -o -name "*.pcap" -o -name "__pycache__" \) -exec rm -rf {} + 2>/dev/null || true
find "$COMMONS" \( -name "*.db" -o -name "*.db-wal" -o -name "*.db-shm" -o -name "*.log" -o -name "__pycache__" \) -exec rm -rf {} + 2>/dev/null || true

echo "=== Step 2.1 Complete ==="
