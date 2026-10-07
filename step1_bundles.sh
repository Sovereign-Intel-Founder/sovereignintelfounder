set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"
BACKUP="$HOME/repository-backups/2026-10-06"

git -C "$SIP" bundle create "$BACKUP/sovereignintelfounder-pre-cleanup.bundle" --all
git -C "$COMMONS" bundle create "$BACKUP/sovereign-seed-commons-pre-cleanup.bundle" --all
echo "=== Step 1.2 Complete ==="
