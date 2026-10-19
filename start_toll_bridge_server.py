import http.server
import socketserver
import sqlite3
import os
import json
from datetime import datetime

PORT = 8080
DB_PATH = "./sovereign-seed-commons/sip_mesh_state.db"

def init_traffic_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bridge_traffic_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_ip TEXT,
            endpoint TEXT,
            payload TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

class TollBridgeHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
        client_ip = self.client_address[0]
        
        # Log incoming request into database
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bridge_traffic_log (client_ip, endpoint, payload)
                VALUES (?, ?, ?);
            """, (client_ip, self.path, post_data))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR logging traffic]: {e}")

        # Respond to client
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_recs = {"status": "accepted", "ingress": "port_8080", "timestamp": str(datetime.now())}
        self.wfile.write(json.dumps(response_recs).encode('utf-8'))

    def do_GET(self):
        self.do_POST() # Handle GETs as pings too

def run():
    init_traffic_table()
    handler = TollBridgeHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[TOLL BRIDGE] Active and listening on port {PORT}. Capturing incoming traffic to ledger.")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
