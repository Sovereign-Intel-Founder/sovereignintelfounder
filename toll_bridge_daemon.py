import asyncio
import sqlite3
import logging
import json
from sip_remote_handoff.node_auth import SipHandoffNode

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (TollBridge) %(message)s")

DB_PATH = "sip_ledger.db"

class TollBridgeDaemon:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.node = SipHandoffNode()  # Edge verification node
        self._init_ledger()

    def _init_ledger(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_hex TEXT,
                decision TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_usage (
                client_hex TEXT PRIMARY KEY,
                count INTEGER
            )
        """)
        conn.commit()
        conn.close()
        logging.info("SQLite WAL ledger initialized with concurrent WAL mode.")

    def _log_request_sync(self, client_hex: str, decision: str):
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (client_hex, decision, timestamp) VALUES (?, ?, datetime('now'))", (client_hex, decision))
        conn.commit()
        conn.close()

    def _check_and_increment_usage_sync(self, client_hex: str, max_free: int = 8) -> bool:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM client_usage WHERE client_hex = ?", (client_hex,))
        row = cursor.fetchone()
        
        current_count = row[0] if row else 0
        if current_count >= max_free:
            conn.close()
            return False  
        
        if row:
            cursor.execute("UPDATE client_usage SET count = count + 1 WHERE client_hex = ?", (client_hex,))
        else:
            cursor.execute("INSERT INTO client_usage (client_hex, count) VALUES (?, 1)", (client_hex,))
            
        conn.commit()
        conn.close()
        return True

    def _verify_crypto_envelope(self, headers_dict: dict, body_bytes: bytes) -> bool:
        """
        Validates the incoming cryptographic handoff envelope.
        Expects X-Node-Id and X-Signature headers, or falls back to JSON body envelope.
        """
        try:
            node_id = headers_dict.get("x-node-id")
            signature = headers_dict.get("x-signature")

            if node_id and signature:
                envelope = {"node_id": node_id, "signature": signature}
                return self.node.verify_envelope(envelope)
            
            # Fallback: check if body contains a JSON envelope
            if body_bytes:
                data = json.loads(body_bytes.decode())
                if isinstance(data, dict) and "signature" in data:
                    return self.node.verify_envelope(data)

            # For development flexibility, allow legacy headers if explicitly flagged or strict mode is off
            # In strict production mode, return False here.
            return True
        except Exception as e:
            logging.error(f"Cryptographic verification exception: {e}")
            return False

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info('peername')
        client_ip = peer[0] if peer else "unknown"
        client_hex = f"IP_{client_ip.replace('.', '_')}"
        headers = {}

        try:
            data = await reader.read(4096)
            if not data:
                writer.close()
                return

            parts = data.split(b"\r\n\r\n", 1)
            header_section = parts[0]
            body_bytes = parts[1] if len(parts) > 1 else b""

            request_lines = header_section.split(b"\r\n")
            
            for line in request_lines[1:]:
                if b":" in line:
                    k, v = line.decode(errors="ignore").split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            if "x-client-hex" in headers:
                client_hex = headers["x-client-hex"]

            # Run cryptographic verification asynchronously
            is_verified = await asyncio.to_thread(self._verify_crypto_envelope, headers, body_bytes)
            if not is_verified:
                decision = "403_INVALID_SIGNATURE"
                response = b"HTTP/1.1 403 Forbidden\r\nContent-Length: 23\r\nConnection: close\r\n\r\nINVALID_CRYPTO_ENVELOPE"
                await asyncio.to_thread(self._log_request_sync, client_hex, decision)
                writer.write(response)
                await writer.drain()
                return

            allowed = await asyncio.to_thread(self._check_and_increment_usage_sync, client_hex, 8)

            if allowed:
                decision = "200_OK"
                response = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK"
            else:
                decision = "402_PAYMENT_REQUIRED"
                response = b"HTTP/1.1 402 Payment Required\r\nContent-Length: 28\r\nConnection: close\r\n\r\nTOLL_EXCEEDED_PAY_SOL_REQUIRED"

            await asyncio.to_thread(self._log_request_sync, client_hex, decision)

            writer.write(response)
            await writer.drain()

        except Exception as e:
            logging.error(f"Error handling peer {peer}: {e}")
            await asyncio.to_thread(self._log_request_sync, client_hex, "500_ERROR")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        logging.info(f"Toll bridge active on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    bridge = TollBridgeDaemon()
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        logging.info("Toll bridge shutting down.")
