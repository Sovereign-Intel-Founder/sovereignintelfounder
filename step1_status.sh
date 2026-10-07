set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"
BACKUP="$HOME/repository-backups/2026-10-06"

mkdir -p "$BACKUP"
chmod 700 "$BACKUP"

test -d "$SIP/.git"
test -d "$COMMONS/.git"

git -C "$SIP" status --short
git -C "$COMMONS" status --short
echo "=== Step 1.1 Complete ==="
