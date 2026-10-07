set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "=== Commons Security Paths ==="
find "$COMMONS" -type f \( -name "*.py" -o -name "*.rs" -o -name "*.go" -o -name "*.c" \) | grep -iE "sec|auth|crypto|sig|verify|handoff|nonce|idempot|lineage|hmac|ed25519" || true

echo "=== Running Commons Tests ==="
cd "$COMMONS"
PYTHONPATH="$COMMONS" pytest tests/ -v || PYTHONPATH="$COMMONS" python3 -m unittest discover -s . -p "*test*.py" || true

echo "=== Removing node_key.bin artifact ==="
find "$SIP" -name "node_key.bin" -exec git -C "$SIP" rm -f {} + 2>/dev/null || true
git -C "$SIP" commit -m "security: remove node_key.bin public binary artifact" || true

echo "=== Step 2 Complete ==="
