import time
import json
import random

def run_dry_run_loop(iterations=5):
    print("[*] Initializing Sovereign Intelligence Protocol Live Telemetry (Dry-Run Mode)")
    print("[*] Target Venues: Multi-node simulated edge ingestion")
    
    for i in range(iterations):
        timestamp = int(time.time() * 1000)
        # Simulate live tick jitter across venues
        ask_a = 100.0 + random.uniform(-0.1, 0.1)
        bid_b = ask_a + random.uniform(-0.05, 0.25)
        
        spread = bid_b - ask_a
        status = "DRY_RUN_FILL" if spread > 0.08 else "SKIPPED_SPREAD_NARROW"
        
        log_entry = {
            "sequence": i + 1,
            "timestamp_ms": timestamp,
            "venue_ask": round(ask_a, 4),
            "venue_bid": round(bid_b, 4),
            "gross_spread": round(spread, 4),
            "decision": status
        }
        
        print(json.dumps(log_entry))
        with open("live_harness/logs/audit_trail.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        time.sleep(0.5)

if __name__ == "__main__":
    run_dry_run_loop()
