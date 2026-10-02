from http.server import HTTPServer, BaseHTTPRequestHandler

class TollBridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        print(f"[RECEIVED PAYLOAD] {body.decode('utf-8', errors='ignore')}")
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b'{"status": "accepted"}')

print("=== Starting Local Toll Bridge Receiver on Port 8000 ===")
server = HTTPServer(('127.0.0.1', 8000), TollBridgeHandler)
server.serve_forever()
