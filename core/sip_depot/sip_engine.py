import time
import json
from sip_depot.ingestion import DirectFeedIngester
from sip_depot.shared_ring import SharedMemoryRingBuffer
from sip_depot.filter_brains import BrainFilterMatrix
from sip_depot.bot_depot import CircuitBreaker, BotDepot

def run_sip_pipeline(total_ticks=5000):
    print("[*] Initializing Sovereign Intelligence Protocol (SIP) Complete Engine...")
    ingester = DirectFeedIngester()
    ring = SharedMemoryRingBuffer(capacity=1024)
    matrix = BrainFilterMatrix()
    breaker = CircuitBreaker(max_drawdown=5000.0)
    depot = BotDepot(pool_size=16)

    metrics = {
        "processed_ticks": 0,
        "approved_ticks": 0,
        "filtered_ticks": 0,
        "dispatched_bots": 0,
        "total_dispatch_latency_ns": 0
    }

    start_time = time.perf_counter()

    for _ in range(total_ticks):
        raw_tick = ingester.poll_raw_feed()
        if not ring.push(raw_tick):
            continue
            
        tick = ring.pop()
        metrics["processed_ticks"] += 1

        if not breaker.check():
            break

        passed, reason = matrix.evaluate(tick)
        if not passed:
            metrics["filtered_ticks"] += 1
            continue

        metrics["approved_ticks"] += 1

        t_start = time.time_ns()
        bot = depot.acquire_bot()
        if bot:
            dispatch_lat = time.time_ns() - t_start
            metrics["dispatched_bots"] += 1
            metrics["total_dispatch_latency_ns"] += dispatch_lat
            depot.return_bot(bot)

    end_time = time.perf_counter()
    duration = end_time - start_time
    throughput = metrics["processed_ticks"] / duration if duration > 0 else 0
    avg_latency = (metrics["total_dispatch_latency_ns"] / metrics["dispatched_bots"]) if metrics["dispatched_bots"] > 0 else 0

    summary = {
        "duration_seconds": round(duration, 4),
        "total_processed": metrics["processed_ticks"],
        "throughput_ops_sec": round(throughput, 2),
        "approved": metrics["approved_ticks"],
        "filtered": metrics["filtered_ticks"],
        "dispatched_bots": metrics["dispatched_bots"],
        "avg_dispatch_latency_ns": round(avg_latency, 2)
    }

    with open("sip_depot/results/engine_benchmark.json", "w") as out:
        json.dump(summary, out, indent=2)

    print(f"[+] SIP Engine Execution Complete.")
    print(f"    - Throughput: {summary['throughput_ops_sec']} events/sec")
    print(f"    - Avg Bot Dispatch Latency: {summary['avg_dispatch_latency_ns']} ns")

if __name__ == "__main__":
    run_sip_pipeline()
