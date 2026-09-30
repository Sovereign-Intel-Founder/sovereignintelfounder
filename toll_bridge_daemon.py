kimport asyncio
import hashlib
import hmac
import json
import mmap
import os
import sqlite3
import struct
import time

DB_PATH = "/home/joshua445/toll_gate/sip_ledger.db"
SECRET_KEY = b"sovereign_intelligence_protocol_secret"
SHM_NAME = "/dev/shm/sip_afxdp_ring"

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

def verify_signature(payload: bytes, signature: str) -> bool:
    if not signature:
        return False
    expected = hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def read_afxdp_shm_telemetry():
    if not os.path.exists(SHM_NAME):
        return {"afxdp_active": False}
    try:
        with open(SHM_NAME, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 48)
            rx_packets, rx_bytes, valid_sigs, invalid_sigs = struct.unpack("QQQQ", mm[:32])
            mm.close()
            return {
                "afxdp_active": True,
                "kernel_rx_packets": rx_packets,
                "kernel_rx_bytes": rx_bytes,
                "kernel_valid_sigs": valid_sigs,
                "kernel_invalid_sigs": invalid_sigs
            }
    except Exception:
        return {"afxdp_active": False}

class TollBridgeServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        init_db()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        start_time = time.perf_counter()
        metrics["total_requests"] += 1

        try:
            request_line = await reader.readline()
            if not request_line:
                writer.close()
                return

            line_str = request_line.decode('utf-8', errors='ignore')
            parts = line_str.split()
            method = parts[0] if len(parts) > 0 else "GET"
            path = parts[1] if len(parts) > 1 else "/"

            headers = {}
            content_length = 0
            while True:
                header_line = await reader.readline()
                if header_line in (b'\r\n', b'\n', b''):
                    break
                header_str = header_line.decode('utf-8', errors='ignore')
                if ':' in header_str:
                    k, v = header_str.split(':', 1)
                    headers[k.strip().lower()] = v.strip()

            if 'content-length' in headers:
                content_length = int(headers['content-length'])

            body = b''
            if content_length > 0:
                body = await reader.readexactly(content_length)

            if path == '/metrics' and method == 'GET':
                latencies = metrics["latencies_ms"]
                p99 = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0.0
                avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
                
                payload_dict = {
                    "status": "online",
                    "total_requests": metrics["total_requests"],
                    "valid_signatures": metrics["valid_signatures"],
                    "invalid_signatures": metrics["invalid_signatures"],
                    "toll_paid_200": metrics["toll_paid_200"],
                    "payment_required_402": metrics["payment_required_402"],
                    "latency_p99_ms": round(p99, 3),
                    "latency_avg_ms": round(avg_lat, 3),
                    "afxdp_kernel_bypass": read_afxdp_shm_telemetry()
                }
                
                resp_payload = json.dumps(payload_dict).encode('utf-8')
                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: application/json\r\n"
                    f"Content-Length: {len(resp_payload)}\r\n"
                    b"Connection: close\r\n\r\n" + resp_payload
                )
                writer.write(response)
                await writer.drain()
                writer.close()
                return

            sig = headers.get('x-sip-signature', '')
            client_id = headers.get('x-client-id', 'UNKNOWN_NODE')
            is_valid = verify_signature(body, sig)

            if is_valid:
                metrics["valid_signatures"] += 1
                metrics["toll_paid_200"] += 1
                status_str = "200_OK"
                body_out = b"OK"
                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(body_out)}\r\n"
                    b"Connection: close\r\n\r\n" + body_out
                )
            else:
                metrics["invalid_signatures"] += 1
                metrics["payment_required_402"] += 1
                status_str = "402_PAYMENT_REQUIRED"
                body_out = b"Payment Required"
                response = (
                    b"HTTP/1.1 402 Payment Required\r\n"
                    b"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(body_out)}\r\n"
                    b"Connection: close\r\n\r\n" + body_out
                )

            writer.write(response)
            await writer.drain()

            latency_ms = (time.perf_counter() - start_time) * 1000.0
            metrics["latencies_ms"].append(latency_ms)
            if len(metrics["latencies_ms"]) > 10000:
                metrics["latencies_ms"] = metrics["latencies_ms"][-5000:]

            asyncio.get_event_loop().run_in_executor(None, log_to_ledger, client_id, status_str, latency_ms)

        except Exception as e:
            pass
        finally:
            writer.close()

    async def run(self):
        server = await asyncio.start_server(
            self.handle_connection, self.host, self.port, reuse_address=True, reuse_port=True
        )
        print(f"Bare-Metal Toll Bridge Daemon listening on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    daemon = TollBridgeServer()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        pass
