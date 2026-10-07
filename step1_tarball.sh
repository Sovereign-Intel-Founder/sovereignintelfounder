set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"
BACKUP="$HOME/repository-backups/2026-10-06"

tar --exclude='.git' \
  --exclude='sovereign_backup_archive' \
  --exclude='*.db' \
  --exclude='*.db-wal' \
  --exclude='*.db-shm' \
  --exclude='*.log' \
  --exclude='*.jsonl' \
  --exclude='*.pcap' \
  --exclude='__pycache__' \
  -czf "$BACKUP/sovereignintelfounder-working-tree-pre-cleanup.tar.gz" \
  -C "$SIP" .

tar --exclude='.git' \
  --exclude='*.db' \
  --exclude='*.db-wal' \
  --exclude='*.db-shm' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  -czf "$BACKUP/sovereign-seed-commons-working-tree-pre-cleanup.tar.gz" \
  -C "$COMMONS" .
echo "=== Step 1.3 Complete ==="
