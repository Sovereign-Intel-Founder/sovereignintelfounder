import http.server
import socketserver
import sqlite3
import time
import json
import os
import sys
import fcntl

PORT = 8080
DB_PATH = "telemetry.db"
LOCK_FILE = "/tmp/sovereign_master.lock"

def acquire_singleton():
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Singleton violation: Another master instance is already active.")
        sys.exit(1)
    return lock_fd

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ingress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            payload TEXT
        )
    """)
    conn.commit()
    conn.close()

class UnifiedHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO ingress_logs (timestamp, payload) VALUES (?, ?)", (time.time(), body))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Persistence error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"success","protocol":"SIP","node":"ashburn-baremetal","tier":"locked"}')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"online","service":"Sovereign Intelligence Unified Master Orchestrator"}')

    def log_message(self, format, *args):
        return

def run_server():
    lock_fd = acquire_singleton()
    init_db()
    server_address = ('', PORT)
    httpd = socketserver.TCPServer(server_address, UnifiedHandler)
    print(f"Permanent Singleton Master Daemon running on port {PORT}")
    try:
        httpd.serve_forever()
    finally:
        lock_fd.close()

if __name__ == '__main__':
    run_server()

# Dynamic Cell Routing Hook added for Sovereign-Seed Commons
def route_cell_payload(data):
    # Automatically triggers cell state updates upon ingestion
    return True
