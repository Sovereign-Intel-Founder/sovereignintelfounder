import socket, json, sys, time

def run_core_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 8080))
    server.listen(128)
    print("[SIP-CORE] Pipeline engine active and listening on port 8080...")

    server.settimeout(3.0)
    try:
        while True:
            try:
                conn, addr = server.accept()
                data = conn.recv(4096)
                if data:
                    packet = json.loads(data.decode().strip())
                    source = packet.get("source_node")
                    ingress = packet.get("ingress", {})
                    print(f"[SIP-CORE] Ingested verified telemetry from node '{source}': payload='{ingress.get('payload')}' (nonce: {ingress.get('nonce')})")
                conn.close()
            except socket.timeout:
                break
    finally:
        server.close()
        print("[SIP-CORE] Core pipeline shut down.")

if __name__ == "__main__":
    run_core_listener()
