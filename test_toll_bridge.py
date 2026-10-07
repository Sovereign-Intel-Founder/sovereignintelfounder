import asyncio, json, hmac, hashlib
with open(".sip_secret", "rb") as f: SECRET_KEY = f.read().strip()
async def test_bridge():
    payload = {"client_id": "FRESH_NODE_001", "status": "active", "latency_ms": 1.25}
    body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    headers = [b"POST / HTTP/1.1", b"Host: 127.0.0.1:8080", b"X-Client-Hex: FRESH_NODE_001", b"X-Node-Id: node_001", f"x-sip-signature: {sig}".encode("utf-8"), f"Content-Length: {len(body)}".encode("utf-8"), b"Connection: close", b"", b""]
    req = b"\r\n".join(headers) + body
    r, w = await asyncio.open_connection("127.0.0.1", 8080)
    w.write(req); await w.drain()
    print("--- BRIDGE RESPONSE ---")
    print((await r.read(1024)).decode(errors="ignore"))
    w.close(); await w.wait_closed()
asyncio.run(test_bridge())
