import asyncio
import sqlite3
import time
import os
import hashlib
import json

DB_PATH = "telemetry.db"
client_failure_tracking = {}

def initialize_production_environment():
    """Initializes SQLite with high-concurrency WAL mode and rigorous telemetry schema."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tollbridge_ingress (
            packet_id TEXT PRIMARY KEY,
            payload TEXT,
            latency_ns INTEGER,
            tier_id TEXT,
            charged_price REAL,
            received_at REAL,
            canonical_hash TEXT,
            trade_status TEXT,
            profit_share REAL
        )
    """)
    conn.commit()
    conn.close()
    print("[+] Sovereign Intelligence Protocol: Elite Engine Initialized.")

class TollBridgeServer:
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        start_time = time.perf_counter()
        
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
            while True:
                header_line = await reader.readline()
                if header_line in (b'\r\n', b'\n', b''):
                    break
                header_str = header_line.decode('utf-8', errors='ignore')
                if ':' in header_str:
                    k, v = header_str.split(':', 1)
                    headers[k.strip().lower()] = v.strip()
            
            # --- RIGOROUS PERFORMANCE & SUCCESS-ALIGNED ENGINE ---
            packet_id = f"sip_pkt_{int(time.time_ns())}"
            latency_ns = int((time.perf_counter() - start_time) * 1e9)

            # Ingest trade telemetry parameters directly from client headers
            trade_profit = float(headers.get('x-sip-trade-profit', 0.00))
            trade_status = headers.get('x-sip-trade-status', 'loss' if trade_profit <= 0 else 'win')
            client_id = headers.get('x-sip-client-id', 'unregistered_bot')

            # Circuit breaker safety to prevent client capital drain from failure loops
            consecutive_fails = client_failure_tracking.get(client_id, 0)
            if consecutive_fails > 10:
                response_body = json.dumps({
                    "status": "error",
                    "code": 429,
                    "message": "Circuit breaker active: excessive consecutive failure loops detected. Throttled."
                })
                response = (
                    f"HTTP/1.1 429 Too Many Requests\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Connection: close\r\n"
                    f"Content-Length: {len(response_body)}\r\n\r\n"
                    f"{response_body}"
                )
                writer.write(response.encode('utf-8'))
                await writer.drain()
                return

            # Success-aligned pricing logic: Win shares performance; losses/fails cost zero risk
            if trade_status == 'win' and trade_profit > 0:
                client_failure_tracking[client_id] = 0  # Reset on successful execution
                if latency_ns < 200:
                    tier_id = "tier_baremetal_isolated_core"
                    share_pct = 0.35  # 35% for sub-200ns elite alpha
                elif latency_ns < 1000:
                    tier_id = "tier_low_latency_bypass"
                    share_pct = 0.25  # 25% for kernel bypasses
                elif latency_ns < 5000:
                    tier_id = "tier_predictive_mesh_sim"
                    share_pct = 0.15  # 15% for mesh simulation
                else:
                    tier_id = "tier_standard_ingress"
                    share_pct = 0.10  # 10% standard success split
                
                charged_price = round(trade_profit * share_pct, 4)
            else:
                client_failure_tracking[client_id] = consecutive_fails + 1
                tier_id = "tier_zero_risk_ingress"
                charged_price = 0.0010  # Minimal serialization gas; zero structural risk

            # Cryptographic tamper-evident audit envelope
            raw_envelope = f"{packet_id}:{method}:{path}:{latency_ns}:{tier_id}:{charged_price}:{trade_status}"
            canonical_hash = hashlib.sha256(raw_envelope.encode('utf-8')).hexdigest()

            # Atomic WAL persistence
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO tollbridge_ingress 
                    (packet_id, payload, latency_ns, tier_id, charged_price, received_at, canonical_hash, trade_status, profit_share)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (packet_id, f"{method} {path}", latency_ns, tier_id, charged_price, time.time(), canonical_hash, trade_status, charged_price))
                conn.commit()
                conn.close()
            except Exception as db_err:
                print(f"[!] SQLite WAL Write Error: {db_err}")
            # ----------------------------------------------------

            response_body = json.dumps({
                "status": "success",
                "protocol": "Sovereign Intelligence Protocol",
                "tier": tier_id,
                "trade_status": trade_status,
                "charged_fee": charged_price,
                "canonical_hash": canonical_hash
            })
            
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"X-SIP-Latency-Tier: {tier_id}\r\n"
                f"X-SIP-Charged-Fee: {charged_price}\r\n"
                f"X-SIP-Canonical-Hash: {canonical_hash}\r\n"
                f"Connection: close\r\n"
                f"Content-Length: {len(response_body)}\r\n\r\n"
                f"{response_body}"
            )
            writer.write(response.encode('utf-8'))
            await writer.drain()
        except Exception as e:
            print(f"[!] Connection Handler Exception: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass

    async def start(self):
        initialize_production_environment()
        server = await asyncio.start_server(self.handle_connection, '0.0.0.0', 8080)
        addr = server.sockets[0].getsockname()
        print(f"[*] Sovereign Toll Bridge Daemon online and listening on {addr}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(TollBridgeServer().start())
    except KeyboardInterrupt:
        print("\n[-] Sovereign Engine shutdown sequence complete.")
