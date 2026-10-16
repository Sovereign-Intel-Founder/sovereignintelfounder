#!/usr/bin/env python3
import os
import sys
import yaml

def main():
    allowed = {"README.md", "MANIFEST.yaml", "PROOF_STANDARD.md"}
    for entry in os.listdir("benchmarks"):
        if os.path.isfile(os.path.join("benchmarks", entry)) and entry not in allowed:
            print(f"Error: Loose top-level file '{entry}'", file=sys.stderr)
            sys.exit(1)
    
    with open("benchmarks/MANIFEST.yaml", "r") as f:
        manifest = yaml.safe_load(f) or {}
    reg_ids = {b.get("id") for b in manifest.get("benchmarks", [])}

    for cat in ["canonical", "experiments"]:
        cat_dir = os.path.join("benchmarks", cat)
        if os.path.exists(cat_dir):
            for b_id in os.listdir(cat_dir):
                if os.path.isdir(os.path.join(cat_dir, b_id)) and b_id not in reg_ids:
                    print(f"Error: Unregistered benchmark '{cat}/{b_id}'", file=sys.stderr)
                    sys.exit(1)
    print("Strict validation PASSED.")

if __name__ == "__main__":
    main()
