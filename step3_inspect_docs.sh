set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "=== SIP Documentation Files ==="
find "$SIP" -maxdepth 2 -name "*.md" -o -name "LICENSE*"

echo "=== Commons Documentation Files ==="
find "$COMMONS" -maxdepth 2 -name "*.md" -o -name "LICENSE*"
echo "=== Step 3.1 Complete ==="
