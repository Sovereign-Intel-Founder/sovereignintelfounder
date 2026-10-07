set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "Removing internal backup archives..."
rm -rf "$SIP/sovereign_backup_archive" 2>/dev/null || true
rm -rf "$COMMONS/sovereign_backup_archive" 2>/dev/null || true

echo "=== Step 2.2 Complete ==="
