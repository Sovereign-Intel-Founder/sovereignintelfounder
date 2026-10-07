set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

git -C "$SIP" add -u
git -C "$SIP" commit -m "chore: purge generated logs and temporary telemetry" || true

git -C "$COMMONS" add -u
git -C "$COMMONS" commit -m "chore: purge temporary database WAL/SHM artifacts" || true

echo "=== Step 2.4 Complete (Block 2 Finished) ==="
