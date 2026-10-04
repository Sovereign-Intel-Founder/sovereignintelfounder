import asyncio
import time
import aiohttp

URL = "http://127.0.0.1:8080"
TOTAL_REQUESTS = 10000
CONCURRENCY = 50

async def worker(session, requests_per_worker, latencies):
    for _ in range(requests_per_worker):
        t0 = time.perfcounter()
        try:
            async with session.get(URL, headers={"X-Client-ID": "bench_worker"}) as resp:
                await resp.read()
                if resp.status == 200:
                    latencies.append((time.perfcounter() - t0) * 1000)
        except Exception:
            pass

async def main():
    latencies = []
    reqs_per_worker = TOTAL_REQUESTS // CONCURRENCY
    
    conn = aiohttp.TCPConnector(limit=CONCURRENCY, keepalive_timeout=60)
    async with aiohttp.ClientSession(connector=conn) as session:
        t_start = time.perfcounter()
        tasks = [worker(session, reqs_per_worker, latencies) for _ in range(CONCURRENCY)]
        await asyncio.gather(*tasks)
        t_end = time.perfcounter()

    duration = t_end - t_start
    latencies.sort()
    
    print(f"\n================ KEEP-ALIVE BENCHMARK ================")
    print(f"Total Requests : {len(latencies)} / {TOTAL_REQUESTS}")
    print(f"Duration       : {duration:.3f} s")
    print(f"Throughput     : {len(latencies) / duration:.2f} req/sec")
    if latencies:
        print(f"Avg Latency    : {sum(latencies) / len(latencies):.3f} ms")
        print(f"P50 Latency    : {latencies[int(len(latencies) * 0.50)]:.3f} ms")
        print(f"P99 Latency    : {latencies[int(len(latencies) * 0.99)]:.3f} ms")
    print(f"======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
