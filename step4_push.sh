set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "Pushing SIP cleanup branch..."
git -C "$SIP" push -u origin repository-cleanup-2026-10-06

echo "Pushing Commons cleanup branch..."
git -C "$COMMONS" push -u origin repository-cleanup-2026-10-06

echo "=== Step 4.2 Complete (All Blocks Finished) ==="
