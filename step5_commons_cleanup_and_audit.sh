set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "=== 1. Removing ACTIVE_TUNNEL.txt and compiled objects in Commons ==="
git -C "$COMMONS" rm -f ACTIVE_TUNNEL.txt 2>/dev/null || true
find "$COMMONS" -name "xdp_ingress.o" -o -name "xdp_setup.o" -exec git -C "$COMMONS" rm -f {} + 2>/dev/null || true
git -C "$COMMONS" commit -m "chore: remove ACTIVE_TUNNEL.txt and tracked compiled object files" || true

echo "=== 2. Auditing Git Tree and History for Secrets & Paths ==="
echo "--- SIP Audit ---"
git -C "$SIP" grep -E "api_key|secret|private_key|wallet|tunnel|/home/joshua445" || true
git -C "$SIP" log --all -S "/home/joshua445" --oneline || true

echo "--- Commons Audit ---"
git -C "$COMMONS" grep -E "api_key|secret|private_key|wallet|tunnel|/home/joshua445" || true
git -C "$COMMONS" log --all -S "/home/joshua445" --oneline || true

echo "=== Step 5 Complete ==="
