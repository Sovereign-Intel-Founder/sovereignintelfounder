import asyncio
import time
import httpx

URL = "http://127.0.0.1:8080/"
TOTAL_REQUESTS = 50000
CONCURRENCY = 500

async def fetch(client, semaphore):
    async with semaphore:
        start = time.perf_counter()
        try:
            response = await client.post(URL, json={"test": "async_load"}, timeout=5.0)
            duration = (time.perf_counter() - start) * 1000.0
            return response.status_code == 200, duration
        except Exception:
            return False, 0.0

async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY)
    limits = httpx.Limits(max_keepalive_connections=CONCURRENCY, max_connections=CONCURRENCY)
    
    print(f"[*] Starting Async Benchmark: {TOTAL_REQUESTS} requests, concurrency {CONCURRENCY}")
    start_all = time.perf_counter()
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [fetch(client, semaphore) for _ in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
    total_duration = time.perf_counter() - start_all
    
    successes = sum(1 for r, _ in results if r)
    errors = TOTAL_REQUESTS - successes
    latencies = [d for r, d in results if r]
    
    rps = TOTAL_REQUESTS / total_duration
    
    print("\n" + "="*40)
    print("       ULTIMATE ASYNC BENCHMARK RESULTS")
    print("="*40)
    print(f"Total Time Elapsed : {total_duration:.4f} seconds")
    print(f"Throughput (RPS)   : {rps:.2f} req/sec")
    print(f"Successful Requests: {successes}")
    print(f"Failed / Errors    : {errors}")
    if latencies:
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        print(f"Latency (p50)      : {p50:.2f} ms")
        print(f"Latency (p95)      : {p95:.2f} ms")
        print(f"Latency (p99)      : {p99:.2f} ms")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())
