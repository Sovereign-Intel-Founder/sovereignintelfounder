set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"

echo "=== SIP Security Paths ==="
find "$SIP" -type f \( -name "*.py" -o -name "*.c" -o -name "*.h" \) | grep -iE "sec|auth|crypto|sig|verify|handoff|nonce|idempot|lineage|hmac|ed25519" || true

echo "=== Running SIP Tests with PYTHONPATH ==="
cd "$SIP"
PYTHONPATH="$SIP" pytest tests/ -v || PYTHONPATH="$SIP" python3 -m unittest discover -s . -p "*test*.py" || true

echo "=== Step 1 Fixed Complete ==="
