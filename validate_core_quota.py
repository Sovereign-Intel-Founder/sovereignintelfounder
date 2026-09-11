#!/usr/bin/env python3
import hashlib
import hmac
import json
import sqlite3
import time
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:8080/v1/ingress/raw"
SECRET_PATH = "/opt/tollbridge_system/.ingress_secret"
DB = "/var/lib/tollbridge-core/toll_bridge.db"

def post(client: str, event_id: str) -> tuple[int, dict]:
    body = json.dumps({"event_id": event_id, "source": "quota-validation", "payload": {"validation_only": True}}, separators=(",", ":")).encode()
    secret = open(SECRET_PATH, "r", encoding="utf-8").read().strip().encode()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    req = Request(URL, data=body, headers={"Content-Type": "application/json", "X-Tollbridge-Signature": sig, "X-Tollbridge-Source": "quota-validation", "X-Client-Token": client}, method="POST")
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read())
    except Exception as exc:
        code = getattr(exc, "code", 0)
        raw = exc.read() if hasattr(exc, "read") else b"{}"
        try: data = json.loads(raw)
        except Exception: data = {"error": str(exc)}
        return code, data

def main() -> None:
    client = f"core-quota-{time.time_ns()}"
    statuses = [post(client, f"core-quota-{i}")[0] for i in range(1, 10)]
    db = sqlite3.connect(DB)
    result = {
        "statuses_1_to_9": statuses,
        "expected": [202] * 8 + [402],
        "quota_clients": db.execute("SELECT COUNT(*) FROM tollbridge_quota_clients").fetchone()[0],
        "pipeline_queued": db.execute("SELECT COUNT(*) FROM pipeline_events WHERE status='queued'").fetchone()[0],
        "pipeline_completed": db.execute("SELECT COUNT(*) FROM pipeline_events WHERE status='completed'").fetchone()[0],
        "journal_mode": db.execute("PRAGMA journal_mode").fetchone()[0],
        "synchronous": db.execute("PRAGMA synchronous").fetchone()[0],
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
