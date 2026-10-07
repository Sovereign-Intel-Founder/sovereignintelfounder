set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"
BACKUP="$HOME/repository-backups/2026-10-06"

git -C "$SIP" switch -c repository-cleanup-2026-10-06
git -C "$COMMONS" switch -c repository-cleanup-2026-10-06

git -C "$SIP" tag pre-cleanup-2026-10-06
git -C "$COMMONS" tag pre-cleanup-2026-10-06

ls -lh "$BACKUP"
echo "=== Step 1.4 Complete (Block 1 Finished) ==="
