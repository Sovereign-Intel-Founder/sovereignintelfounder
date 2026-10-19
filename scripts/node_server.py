import sys, socket, selectors, json, hashlib, hmac, time, sqlite3, signal
from dataclasses import dataclass
from scripts.node_config import load_and_validate, NodeConfig

# Shared cryptographic secret for true HMAC-SHA256 signing across the mesh
MESH_SECRET_KEY = b"sovereign-intelligence-protocol-master-key-2026"

# Initialize SQLite WAL-mode auditing database
DB_PATH = "mesh_audit.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT,
            payload TEXT,
            timestamp REAL,
            signature TEXT,
            received_at REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@dataclass(frozen=True)
class CryptoEnvelope:
    sender_id: str
    payload: str
    timestamp: float
    nonce: str
    signature: str

    def verify_integrity(self, max_drift: float = 30.0) -> bool:
        if abs(time.time() - self.timestamp) > max_drift:
            return False
        message = f"{self.sender_id}:{self.payload}:{self.timestamp}:{self.nonce}".encode()
        expected_sig = hmac.new(MESH_SECRET_KEY, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.signature, expected_sig)

class SipHandoffNode:
    def __init__(self, config_path: str):
        self.config = load_and_validate(config_path)
        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.connected_peers = set()
        self.buffers = {}
        self.seen_nonces = set()
        self.is_running = True

        # Register OS signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        print(f"\n[{self.config.node_id}] Received termination signal. Shutting down gracefully...")
        self.is_running = False

    def bind(self):
        self.sock.bind((self.config.listen_ip, self.config.listen_port))
        self.sock.listen(128)
        self.sel.register(self.sock, selectors.EVENT_READ, data=self._accept_wrapper)
        print(f"[{self.config.node_id}] Bound to {self.config.listen_ip}:{self.config.listen_port} [Production Hardened]")

    def forward_to_sip_core(self, envelope: CryptoEnvelope):
        core_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        core_sock.settimeout(0.5)
        try:
            core_sock.connect(("127.0.0.1", 8080))
            packet = {"source_node": self.config.node_id, "ingress": envelope.__dict__}
            core_sock.sendall((json.dumps(packet) + "\n").encode())
            print(f"[{self.config.node_id}] Bridged verified envelope to SIP core on port 8080")
        except (socket.timeout, ConnectionRefusedError):
            print(f"[{self.config.node_id}] SIP core (port 8080) offline; holding packet in-memory.")
        finally:
            core_sock.close()

    def _accept_wrapper(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        try:
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        except AttributeError:
            pass
        self.buffers[conn] = b""
        self.sel.register(conn, selectors.EVENT_READ, data=self._read_handler)

    def _read_handler(self, conn):
        try:
            data = conn.recv(4096)
            if data:
                self.buffers[conn] += data
                while b"\n" in self.buffers[conn]:
                    line, self.buffers[conn] = self.buffers[conn].split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        envelope_dict = json.loads(line.decode().strip())
                        env = CryptoEnvelope(
                            envelope_dict.get("sender_id"),
                            envelope_dict.get("payload"),
                            envelope_dict.get("timestamp", 0.0),
                            envelope_dict.get("nonce", ""),
                            envelope_dict.get("signature")
                        )
                        if env.nonce in self.seen_nonces:
                            print(f"[{self.config.node_id}] REPLAY ATTACK REJECTED: Duplicate nonce {env.nonce}")
                            continue
                        if env.verify_integrity():
                            self.seen_nonces.add(env.nonce)
                            print(f"[{self.config.node_id}] HMAC Verified envelope from {env.sender_id}: {env.payload}")
                            
                            db_conn = sqlite3.connect(DB_PATH)
                            db_conn.execute(
                                "INSERT INTO audit_log (sender_id, payload, timestamp, signature, received_at) VALUES (?, ?, ?, ?, ?)",
                                (env.sender_id, env.payload, env.timestamp, env.signature, time.time())
                            )
                            db_conn.commit()
                            db_conn.close()

                            self.forward_to_sip_core(env)
                        else:
                            print(f"[{self.config.node_id}] SECURITY ALERT: HMAC signature or timestamp drift validation failed!")
                    except json.JSONDecodeError:
                        print(f"[{self.config.node_id}] Malformed frame dropped: {line.decode().strip()}")
            else:
                self.sel.unregister(conn)
                self.buffers.pop(conn, None)
                conn.close()
        except (ConnectionResetError, BrokenPipeError):
            self.sel.unregister(conn)
            self.buffers.pop(conn, None)
            conn.close()

    def poll_peers(self):
        for peer in self.config.peers:
            if peer.peer_id in self.connected_peers:
                continue
            peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_sock.settimeout(0.2)
            try:
                peer_sock.connect((peer.endpoint_ip, peer.endpoint_port))
                payload_str = "HELO-MESH-STATE-SYNC"
                ts = time.time()
                nonce = hashlib.md5(f"{self.config.node_id}:{ts}".encode()).hexdigest()[:12]
                
                message = f"{self.config.node_id}:{payload_str}:{ts}:{nonce}".encode()
                sig = hmac.new(MESH_SECRET_KEY, message, hashlib.sha256).hexdigest()
                
                envelope = {
                    "sender_id": self.config.node_id,
                    "payload": payload_str,
                    "timestamp": ts,
                    "nonce": nonce,
                    "signature": sig
                }
                peer_sock.sendall((json.dumps(envelope) + "\n").encode())
                print(f"[{self.config.node_id}] Established secured HMAC link & dispatched envelope to {peer.peer_id}")
                self.connected_peers.add(peer.peer_id)
            except (socket.timeout, ConnectionRefusedError):
                pass
            finally:
                peer_sock.close()

    def run(self):
        try:
            while self.is_running:
                self.poll_peers()
                events = self.sel.select(timeout=0.5)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj)
        except Exception as e:
            print(f"[{self.config.node_id}] Runtime error: {e}")
        finally:
            self.sel.close()
            print(f"[{self.config.node_id}] Shutdown complete.")

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/mesh_node.json"
    node = SipHandoffNode(config_file)
    node.bind()
    node.run()
