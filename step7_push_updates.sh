set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "Pushing updated SIP cleanup branch..."
git -C "$SIP" push origin repository-cleanup-2026-10-06

echo "Pushing updated Commons cleanup branch..."
git -C "$COMMONS" push origin repository-cleanup-2026-10-06

echo "=== Step 7 Complete ==="
