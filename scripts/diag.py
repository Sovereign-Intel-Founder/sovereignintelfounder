import socket, time

host = '127.0.0.1'
port = 8080

print("Running connection diagnostic...")
try:
    start = time.perf_counter_ns()
    s = socket.create_connection((host, port), timeout=1.0)
    print("Connected successfully!")
    s.close()
except Exception as e:
    print(f"Connection failed: {type(e).__name__} -> {e}")
