set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "=== SIP Git Status & Recent Commits ==="
git -C "$SIP" status
git -C "$SIP" log -n 3 --oneline

echo "=== Commons Git Status & Recent Commits ==="
git -C "$COMMONS" status
git -C "$COMMONS" log -n 3 --oneline

echo "=== Step 4.1 Complete ==="
