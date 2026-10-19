import os
import sqlite3
import json
import time
import socket
import threading

DB_PATH = "telemetry.db"
HOST = "0.0.0.0"
PORT = 8080

def initialize_master_schema():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS protocol_cells (
            cell_id TEXT PRIMARY KEY,
            status TEXT,
            task_manifest TEXT,
            updated_at REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_returns (
            evidence_id TEXT PRIMARY KEY,
            cell_id TEXT,
            checksum TEXT,
            logged_at REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tollbridge_ingress (
            packet_id TEXT PRIMARY KEY,
            payload TEXT,
            latency_ns INTEGER,
            received_at REAL
        )
    """)
    conn.commit()
    conn.close()
    print("[+] Master SQLite WAL schema verified and initialized.")

def run_unified_daemon():
    initialize_master_schema()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(128)
    print(f"[+] Sovereign Intelligence Protocol unified daemon active on port {PORT}")

    def handle_client(client_sock, addr):
        start_ns = time.time_ns()
        try:
            data = client_sock.recv(4096)
            if not data:
                return
            latency_ns = time.time_ns() - start_ns
            packet_id = f"pkt_{addr[1]}_{time.time_ns()}"
            payload = data.decode('utf-8', errors='ignore')

            # Write ingestion event to WAL db sharded pipeline
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            conn.execute(
                "INSERT OR REPLACE INTO tollbridge_ingress (packet_id, payload, latency_ns, received_at) VALUES (?, ?, ?, ?)",
                (packet_id, payload, latency_ns, time.time())
            )
            conn.commit()
            conn.close()

            client_sock.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"SUCCESS\",\"packet_id\":\"" + packet_id.encode() + b"\"}\n")
        except Exception as e:
            print(f"[-] Ingestion error: {e}")
        finally:
            client_sock.close()

    while True:
        sock, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(sock, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    run_unified_daemon()
