#!/usr/bin/env python3
import os
import sys
import argparse
import yaml

def main():
    parser = argparse.ArgumentParser(description="Create extensible benchmark.")
    parser.add_argument("--id", required=True, help="Unique benchmark ID")
    parser.add_argument("--category", required=True, choices=["canonical", "experiments", "historical"])
    parser.add_argument("--description", required=True, help="Short description")
    args = parser.parse_args()

    bench_id = args.id
    category = args.category
    target_dir = os.path.join("benchmarks", category, bench_id)

    if os.path.exists(target_dir):
        print(f"Error: '{bench_id}' already exists.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(os.path.join("benchmarks", "results", bench_id), exist_ok=True)

    with open(os.path.join(target_dir, "README.md"), "w") as f:
        f.write(f"# Benchmark: {bench_id}\n\n## Description\n{args.description}\n")

    with open(os.path.join(target_dir, "run.sh"), "w") as f:
        f.write("#!/usr/bin/env bash\nset -euo pipefail\necho 'Running " + bench_id + "'\n")
    os.chmod(os.path.join(target_dir, "run.sh"), 0o755)

    manifest_path = "benchmarks/MANIFEST.yaml"
    manifest_data = {"benchmarks": []}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            try: manifest_data = yaml.safe_load(f) or {"benchmarks": []}
            except Exception: pass

    if not any(b.get("id") == bench_id for b in manifest_data.get("benchmarks", [])):
        manifest_data["benchmarks"].append({
            "id": bench_id, "version": "v1", "category": category,
            "evidence_class": "B" if category == "canonical" else "C",
            "source_path": f"benchmarks/{category}/{bench_id}/"
        })
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f, sort_keys=False)
    print(f"Created benchmark '{bench_id}' successfully.")

if __name__ == "__main__":
    main()
