#!/usr/bin/env python3
import json
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:4021/v1/sip/ingest"
THREADS = 30
EVENTS = 100

def post(client, event_id):
    body = json.dumps({"event_id": event_id, "source": "sip-live", "payload": {"synthetic_validation": True}}).encode()
    req = Request(URL, data=body, headers={"Content-Type": "application/json", "X-Client-Token": client}, method="POST")
    t0 = time.perf_counter()
    try:
        with urlopen(req, timeout=10) as r:
            return r.status, (time.perf_counter() - t0) * 1000
    except Exception as e:
        return getattr(e, "code", 0), (time.perf_counter() - t0) * 1000

def main():
    boundary_client = f"boundary-{time.time_ns()}"
    boundary = [post(boundary_client, f"boundary-{i}")[0] for i in range(1, 10)]
    started = time.perf_counter()
    def worker(t):
        client = f"load-{t}-{time.time_ns()}"
        return [post(client, f"load-{t}-{i}") for i in range(EVENTS)]
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        rows = [item for group in pool.map(worker, range(THREADS)) for item in group]
    elapsed = time.perf_counter() - started
    codes = {}
    lats = sorted(lat for code, lat in rows)
    for code, _ in rows: codes[str(code)] = codes.get(str(code), 0) + 1
    db = sqlite3.connect("/var/lib/tollbridge-core/toll_bridge.db")
    result = {
        "boundary_statuses_1_to_9": boundary,
        "load_total": len(rows),
        "load_statuses": codes,
        "elapsed_seconds": round(elapsed, 6),
        "throughput_events_per_second": round(len(rows) / elapsed, 3),
        "latency_ms": {"min": round(lats[0], 3), "p50": round(lats[len(lats)//2], 3), "p95": round(lats[int(len(lats)*.95)-1], 3), "p99": round(lats[int(len(lats)*.99)-1], 3), "max": round(lats[-1], 3)},
        "sqlite": {"journal_mode": db.execute("PRAGMA journal_mode").fetchone()[0], "synchronous": db.execute("PRAGMA synchronous").fetchone()[0], "pipeline_rows": db.execute("SELECT COUNT(*) FROM pipeline_events").fetchone()[0], "queued_rows": db.execute("SELECT COUNT(*) FROM pipeline_events WHERE status='queued'").fetchone()[0]},
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
