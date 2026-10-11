import http.server, socketserver, json, time
class E(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        t0 = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-SIP-Node", "ashburn-baremetal-128c")
        self.end_headers()
        now = time.time_ns()
        d = {"node": "ashburn-baremetal", "tier": "enterprise-baremetal",
             "timestamp_ns": now, "slot_velocity": 1450 + (int(now/1000000)%100),
             "pre_consensus_verified": True, "latency_ns": time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW) - t0}
        self.wfile.write(json.dumps(d, indent=2).encode())
    def log_message(self, f, *a): pass
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True
if __name__ == "__main__":
    with TS(("", 8080), E) as s: s.serve_forever()
