import asyncio
import hashlib
import hmac
import json
import sqlite3
import time
from aiohttp import web

# Database & Telemetry State
DB_PATH = "/home/joshua445/toll_gate/sip_ledger.db"
SECRET_KEY = b"sovereign_intelligence_protocol_secret"

metrics = {
    "total_requests": 0,
    "valid_signatures": 0,
    "invalid_signatures": 0,
    "toll_paid_200": 0,
    "payment_required_402": 0,
    "latencies_ms": []
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            status TEXT,
            latency_ms REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def verify_signature(payload: bytes, signature: str) -> bool:
    if not signature:
        return False
    expected = hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def log_to_ledger(client_id: str, status: str, latency_ms: float):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("INSERT INTO requests (client_id, status, latency_ms) VALUES (?, ?, ?)",
                    (client_id, status, latency_ms))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ledger Write Error: {e}")

async def handle_ingress(request):
    start_time = time.perf_counter()
    metrics["total_requests"] += 1
    
    body = await request.read()
    sig = request.headers.get("X-SIP-Signature", "")
    client_id = request.headers.get("X-Client-ID", "UNKNOWN_NODE")
    
    is_valid = verify_signature(body, sig)
    if is_valid:
        metrics["valid_signatures"] += 1
        status_code = 200
        status_str = "200_OK"
        metrics["toll_paid_200"] += 1
        resp = web.Response(text="OK", status=200)
    else:
        metrics["invalid_signatures"] += 1
        status_code = 402
        status_str = "402_PAYMENT_REQUIRED"
        metrics["payment_required_402"] += 1
        resp = web.Response(text="Payment Required / Invalid Signature", status=402)
        
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    metrics["latencies_ms"].append(latency_ms)
    if len(metrics["latencies_ms"]) > 10000:
        metrics["latencies_ms"] = metrics["latencies_ms"][-5000:]
        
    # Asynchronous ledger logging
    asyncio.get_event_loop().run_in_executor(None, log_to_ledger, client_id, status_str, latency_ms)
    return resp

async def handle_metrics(request):
    latencies = metrics["latencies_ms"]
    p99 = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0.0
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    
    payload = {
        "status": "online",
        "total_requests": metrics["total_requests"],
        "valid_signatures": metrics["valid_signatures"],
        "invalid_signatures": metrics["invalid_signatures"],
        "toll_paid_200": metrics["toll_paid_200"],
        "payment_required_402": metrics["payment_required_402"],
        "latency_p99_ms": round(p99, 3),
        "latency_avg_ms": round(avg_lat, 3)
    }
    return web.json_response(payload)

async def init_app():
    init_db()
    app = web.Application()
    app.router.add_post('/', handle_ingress)
    app.router.add_get('/', handle_ingress)
    app.router.add_get('/metrics', handle_metrics)
    return app

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', 8080, reuse_address=True, reuse_port=True)
    loop.run_until_complete(site.start())
    print("Sovereign Toll Bridge Daemon running with Cryptographic Engine & /metrics on port 8080")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
