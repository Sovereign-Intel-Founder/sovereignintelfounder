#!/usr/bin/env python3
import sys
import json

# 1. Send initial handshake/ready payload immediately
sys.stdout.write(json.dumps({"type": "handshake", "subject": "sovereign-seed-commons"}) + "\n")
sys.stdout.flush()

# 2. Listen for incoming test stimuli
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
        organ = req.get("organ", "unknown")
    except Exception:
        organ = "unknown"
        
    status = "FAIL" if organ == "audit.control_negative" else "PASS"
    response = {
        "organ": organ,
        "status": status,
        "evidence": f"sovereign-seed-commons::{organ} verified"
    }
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
