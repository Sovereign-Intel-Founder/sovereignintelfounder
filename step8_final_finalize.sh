set -e
SIP="/home/joshua445/sovereign_workspace/sovereign-intelligence/sovereignintelfounder"
COMMONS="/home/joshua445/sovereign_workspace/sovereign-seed-commons"

echo "=== 1. SIP Final Cleanup & Validation ==="
cd "$SIP"
git checkout repository-cleanup-2026-10-06
find . -name "*.log" -o -name "*.jsonl" -not -path "./tests/*" -delete 2>/dev/null || true

make clean || true
make all || true
make test || true
make sanitize || true
make audit || true

git add -A
git commit -m "chore: finalize professional repository cleanup" || true

echo "=== 2. Commons Final Cleanup & Validation ==="
cd "$COMMONS"
git checkout repository-cleanup-2026-10-06
rm -f ACTIVE_TUNNEL.txt 2>/dev/null || true
find . -name "xdp_ingress.o" -o -name "xdp_setup.o" -delete 2>/dev/null || true
find . -name "*.log" -o -name "*.jsonl" -delete 2>/dev/null || true

python3 -m unittest discover -s . -p 'test_*.py' -v || true
python3 -m pytest tests tollbridge_system/tests -q || true

git add -A
git commit -m "chore: finalize professional repository cleanup" || true

echo "=== 3. Pushing Updated Cleanup Branches ==="
git -C "$SIP" push origin repository-cleanup-2026-10-06
git -C "$COMMONS" push origin repository-cleanup-2026-10-06

echo "=== 4. Opening Pull Requests ==="
cd "$SIP"
gh pr create --title "chore: curate SIP repository for professional development" --base main --head repository-cleanup-2026-10-06 --body "Final professional curation and documentation for Sovereign Intelligence Protocol." || echo "PR creation skipped / handled via web UI"

cd "$COMMONS"
gh pr create --title "chore: curate Commons repository for professional development" --base main --head repository-cleanup-2026-10-06 --body "Final professional curation and documentation for Sovereign Seed Commons." || echo "PR creation skipped / handled via web UI"

echo "=== Finalization Complete ==="
