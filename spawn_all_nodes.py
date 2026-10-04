import pathlib
import os

commons_paths = [
    pathlib.Path("/home/joshua445/sovereign-seed-commons"),
    pathlib.Path("/home/joshua445/sovereign-intelligence/sovereign-seed-commons"),
    pathlib.Path("/home/joshua445/sovereign-xdp-shield/sovereign-seed-commons")
]

print("=== Spawning Maximum Protocol Nodes ===")
node_count = 0
for base_path in commons_paths:
    if base_path.exists():
        for i in range(4):  # Spin up 4 active node slots per environment
            node_dir = base_path / f"cell_node_{i}"
            node_dir.mkdir(exist_ok=True)
            manifest = node_dir / "manifest.json"
            manifest.write_text(f'{{"node_id": "cell_{base_path.name}_{i}", "status": "ACTIVE", "telemetry_port": {8010 + node_count}}}')
            print(f"[SPAWNED] Node cell_{base_path.name}_{i} at {node_dir}")
            node_count += 1

print(f"\nTotal active nodes registered across workspace: {node_count}")
