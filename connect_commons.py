import pathlib
import json

commons_paths = [
    pathlib.Path("/home/joshua445/sovereign-seed-commons"),
    pathlib.Path("/home/joshua445/sovereign-intelligence/sovereign-seed-commons"),
    pathlib.Path("/home/joshua445/sovereign-xdp-shield/sovereign-seed-commons")
]

print("=== Connecting Sovereign Seed Commons Nodes ===")
for path in commons_paths:
    if path.exists():
        print(f"[CONNECTED] Active node cluster found at: {path}")
    else:
        print(f"[SKIPPED] Path not present: {path}")
