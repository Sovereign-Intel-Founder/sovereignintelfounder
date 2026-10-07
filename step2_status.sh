set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "=== SIP Git Status ==="
git -C "$SIP" status --short

echo "=== Commons Git Status ==="
git -C "$COMMONS" status --short
echo "=== Step 2.3 Complete ==="
