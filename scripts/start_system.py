import sqlite3
import http.server
import socketserver
import time

DB_FILE = "telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
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

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class TelemetryHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO ingress_logs (timestamp, payload) VALUES (?, ?)", (time.time(), body))
        conn.commit()
        conn.close()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "persisted"}')
        
    def log_message(self, format, *args):
        pass

def run_server():
    init_db()
    server = ThreadingHTTPServer(('127.0.0.1', 8080), TelemetryHandler)
    print("Unified Toll Bridge & WAL Persistence active on http://127.0.0.1:8080")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
