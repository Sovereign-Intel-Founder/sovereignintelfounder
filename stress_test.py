import urllib.request
import concurrent.futures
import time

URL = "http://127.0.0.1:8080/"
TOTAL_REQUESTS = 200
CONCURRENCY = 20

def hit_bridge(i):
    client_hex = f"stress_bot_{i % 5:03d}"
    req = urllib.request.Request(URL, headers={"X-Client-Hex": client_hex})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = 500
    duration = time.perf_counter() - start
    return code, duration

def main():
    print(f"=== STRESS TESTING BRIDGE: {TOTAL_REQUESTS} requests, concurrency={CONCURRENCY} ===")
    start_total = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        results = list(executor.map(hit_bridge, range(TOTAL_REQUESTS)))
        
    total_time = time.perf_counter() - start_total
    codes = [r[0] for r in results]
    print(f"Completed in {total_time:.3f}s | Status distribution: 200={codes.count(200)}, 402={codes.count(402)}")

if __name__ == "__main__":
    main()
