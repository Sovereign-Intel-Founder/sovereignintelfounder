import socket
import select
import time
import json

HOST = '0.0.0.0'
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind((HOST, PORT))
server.listen(128)
server.setblocking(False)

epoll = select.epoll()
epoll.register(server.fileno(), select.EPOLLIN)

connections = {}
requests_cache = {}

print(f"[APEX CORE] Zero-Latency Ingress Reactor active on port {PORT}", flush=True)

try:
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            if fileno == server.fileno():
                conn, addr = server.accept()
                conn.setblocking(False)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLOUT)
                connections[conn.fileno()] = conn
                requests_cache[conn.fileno()] = b""
            elif event & select.EPOLLIN:
                conn = connections[fileno]
                try:
                    data = conn.recv(4096)
                    if data:
                        requests_cache[fileno] += data
                    else:
                        epoll.modify(fileno, select.EPOLLOUT)
                except BlockingIOError:
                    pass
            elif event & select.EPOLLOUT:
                conn = connections[fileno]
                raw_data = requests_cache.get(fileno, b"")
                
                ts_ns = time.time_ns()
                receipt_id = f"rcpt_{ts_ns}"
                
                response_body = json.dumps({
                    "status": "apex_acknowledged",
                    "receipt_id": receipt_id,
                    "tier": "free",
                    "latency_ns": ts_ns
                })
                
                http_response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(response_body)}\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                    f"{response_body}"
                )
                
                try:
                    conn.sendall(http_response.encode('utf-8'))
                except Exception:
                    pass
                
                epoll.unregister(fileno)
                conn.close()
                del connections[fileno]
                del requests_cache[fileno]
finally:
    epoll.unregister(server.fileno())
    epoll.close()
    server.close()
