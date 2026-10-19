# ==============================================================================
# SYNTHETIC PAPER-TRADING DRY-RUN HARNESS
# ==============================================================================
# DESCRIPTION:
# A deterministic local dry-run paper-trading telemetry generator.
# 
# EXPLICIT NOTICE:
# - NO venue, exchange API, wallet, key, or signing mechanism is connected.
# - NO real orders, transactions, or broadcasts are submitted.
# - Prices and fills are generated via seeded synthetic simulation.
# ==============================================================================

import random
import json
import time
from pathlib import Path

def run_paper_trader(seed=42, iterations=100):
    random.seed(seed)
    audit_path = Path("live_harness/logs/audit_trail.jsonl")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    
    records = []
    for i in range(iterations):
        record = {
            "timestamp": time.time(),
            "iteration": i,
            "seed": seed,
            "classification": "Synthetic paper-trading dry-run telemetry",
            "venue": "LOCAL_DRY_RUN_STUB",
            "simulated_fill": "DRY_RUN_FILL",
            "price": round(random.uniform(100.0, 200.0), 2)
        }
        records.append(record)
        
    with open(audit_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"[+] Generated {iterations} deterministic paper-trading dry-run audit records with seed {seed}.")

if __name__ == "__main__":
    run_paper_trader()
