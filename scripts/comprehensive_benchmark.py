import time
import threading
import statistics
import requests

URL = 'http://127.0.0.1:8080/'
TOTAL_REQUESTS = 20000
CONCURRENCY = 100

latencies = []
latencies_lock = threading.Lock()
errors = 0
errors_lock = threading.Lock()

def worker(num_requests):
    global errors
    session = requests.Session()
    for _ in range(num_requests):
        start_time = time.perf_counter()
        try:
            resp = session.post(URL, json={"test": "comprehensive_load", "metric": "latency"}, timeout=3)
            duration = (time.perf_counter() - start_time) * 1000.0
            
            if resp.status_code == 200:
                with latencies_lock:
                    latencies.append(duration)
            else:
                with errors_lock:
                    errors += 1
        except Exception:
            with errors_lock:
                errors += 1

def run_comprehensive_suite():
    print(f"[*] Initializing Full-Spectrum Benchmark Suite")
    print(f"[*] Target: {URL}")
    print(f"[*] Total Requests: {TOTAL_REQUESTS} | Concurrency Level: {CONCURRENCY}")
    
    reqs_per_thread = TOTAL_REQUESTS // CONCURRENCY
    threads = []
    
    start_all = time.perf_counter()
    for _ in range(CONCURRENCY):
        t = threading.Thread(target=worker, args=(reqs_per_thread,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    total_duration = time.perf_counter() - start_all
    rps = TOTAL_REQUESTS / total_duration
    
    print("\n" + "="*40)
    print("       BENCHMARK RESULTS SUMMARY")
    print("="*40)
    print(f"Total Time Elapsed : {total_duration:.4f} seconds")
    print(f"Throughput (RPS)   : {rps:.2f} req/sec")
    print(f"Successful Requests: {len(latencies)}")
    print(f"Failed / Errors    : {errors}")
    
    if latencies:
        print(f"Latency (p50)      : {statistics.median(latencies):.2f} ms")
        print(f"Latency (p95)      : {statistics.quantiles(latencies, n=100)[94]:.2f} ms")
        print(f"Latency (p99)      : {statistics.quantiles(latencies, n=100)[98]:.2f} ms")
        print(f"Latency (Min)      : {min(latencies):.2f} ms")
        print(f"Latency (Max)      : {max(latencies):.2f} ms")
    print("="*40)

if __name__ == "__main__":
    run_comprehensive_suite()
