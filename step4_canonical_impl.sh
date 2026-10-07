set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

cat << 'DOC_EOF' > "$SIP/docs/CANONICAL_IMPLEMENTATIONS.md"
# Canonical Implementations

Authoritative security implementations for the Sovereign Intelligence Protocol:
- **SIP Ingress & Authentication**: Authoritative HMAC validation pipelines.
- **Remote Handoff & Verification**: `sip_remote_handoff` validation suites.
- **Replay Prevention & Nonce**: Active timestamp and nonce checking logic.
- **Idempotency**: SQLite WAL-backed durable transaction logs.
DOC_EOF

cat << 'DOC_EOF' > "$COMMONS/docs/CANONICAL_IMPLEMENTATIONS.md"
# Canonical Implementations

Authoritative security implementations for Sovereign Seed Commons:
- **Envelope Validation**: Ed25519 signature checks on protocol cell returns.
- **Evidence Validation**: Cryptographic proof verification pipelines.
DOC_EOF

git -C "$SIP" add docs/CANONICAL_IMPLEMENTATIONS.md
git -C "$SIP" commit -m "docs: add canonical implementations documentation" || true
git -C "$COMMONS" add docs/CANONICAL_IMPLEMENTATIONS.md
git -C "$COMMONS" commit -m "docs: add canonical implementations documentation" || true
echo "=== Step 4 Complete ==="
