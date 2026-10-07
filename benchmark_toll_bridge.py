#!/usr/bin/env python3
import asyncio
import time
import statistics

HOST = "127.0.0.1"
PORT = 8080
CONCURRENCY = 50
REQUESTS_PER_WORKER = 200

async def send_request(worker_id: int):
    latencies = []
    payload = f'{{"worker_id": {worker_id}, "timestamp": {time.time()}}}'.encode("utf-8")
    req_headers = (
        f"POST / HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"X-SIP-Signature: DEV_TEST_BYPASS\r\n"
        f"X-Client-ID: benchmark_worker_{worker_id}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(payload)}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode("utf-8") + payload

    for _ in range(REQUESTS_PER_WORKER):
        t0 = time.perf_counter()
        try:
            reader, writer = await asyncio.open_connection(HOST, PORT)
            writer.write(req_headers)
            await writer.drain()
            resp = await reader.read(1024)
            writer.close()
            await writer.wait_closed()
            if b"200 OK" in resp:
                latencies.append((time.perf_counter() - t0) * 1000.0)
        except Exception:
            pass
    return latencies

async def main():
    total_expected = CONCURRENCY * REQUESTS_PER_WORKER
    print(f"Starting SIP Benchmark: {CONCURRENCY} workers, {total_expected} total requests...")
    
    start_time = time.perf_counter()
    tasks = [send_request(i) for i in range(CONCURRENCY)]
    results = await asyncio.gather(*tasks)
    duration = time.perf_counter() - start_time
    
    all_latencies = [l for worker_res in results for l in worker_res]
    total_reqs = len(all_latencies)
    
    if total_reqs > 0:
        rps = total_reqs / duration
        avg_lat = statistics.mean(all_latencies)
        p50 = statistics.median(all_latencies)
        all_latencies.sort()
        p99_idx = min(int(len(all_latencies) * 0.99), len(all_latencies) - 1)
        p99 = all_latencies[p99_idx]
        
        print("\n================ BENCHMARK RESULTS ================")
        print(f"Total Successful Requests : {total_reqs} / {total_expected}")
        print(f"Execution Time            : {duration:.2f} seconds")
        print(f"Throughput                : {rps:.2f} req/sec")
        print(f"Average Latency           : {avg_lat:.2f} ms")
        print(f"P50 Latency               : {p50:.2f} ms")
        print(f"P99 Latency               : {p99:.2f} ms")
        print("===================================================\n")
    else:
        print("Benchmark failed: No successful responses received.")

if __name__ == "__main__":
    asyncio.run(main())
