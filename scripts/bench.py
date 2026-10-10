import socket, time, statistics

latencies = []
host = '127.0.0.1'
port = 8080

print("Starting RTT benchmark loop...")
for i in range(1000):
    start = time.perf_counter_ns()
    try:
        s = socket.create_connection((host, port), timeout=0.2)
        s.close()
        end = time.perf_counter_ns()
        latencies.append((end - start) / 1000.0)
    except Exception:
        pass
    
    # Print progress every 100 iterations so you aren't left guessing
    if (i + 1) % 100 == 0:
        print(f"Progress: {i + 1}/1000 samples collected...")

if latencies:
    print(f"\n--- BENCHMARK RESULTS ---")
    print(f"Samples: {len(latencies)}")
    print(f"Mean RTT: {statistics.mean(latencies):.2f} us")
    print(f"P99 RTT:  {sorted(latencies)[int(len(latencies)*0.99)]:.2f} us")
else:
    print("\n[!] Error: No successful connections established to port 8080.")
