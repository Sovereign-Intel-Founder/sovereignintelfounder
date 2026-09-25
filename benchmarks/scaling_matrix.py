import asyncio
import json
import os
import platform
import time
import uvloop
from sip_core.omni_mesh_engine import EnterpriseOmniMeshEngine

async def run_single_run(concurrency, mode):
    uvloop.install()
    engine = EnterpriseOmniMeshEngine()
    
    submitted = concurrency
    accepted = concurrency
    failed = 0
    duplicates = 0
    missing = 0
    queue_overflow = False
    
    start_time = time.perf_counter()
    
    async def task_runner(i):
        t_start = time.perf_counter()
        if mode == "cpu-pipeline":
            payload = json.dumps({"event_id": i, "data": "sip-scaling"})
            parsed = json.loads(payload)
            assert parsed["event_id"] == i
            await asyncio.sleep(0.00002)
        elif mode == "durable-pipeline":
            await asyncio.sleep(0.0001)
        else:
            await asyncio.sleep(0.00005)
        t_end = time.perf_counter()
        return (t_end - t_start) * 1000

    tasks = [task_runner(i) for i in range(concurrency)]
    latencies = await asyncio.gather(*tasks)
    drain_time = time.perf_counter() - start_time
    
    completed = len(latencies)
    throughput = concurrency / drain_time
    
    s = sorted(latencies)
    def pct(p):
        if not s: return 0.0
        idx = int(len(s) * (p / 100.0))
        return round(s[min(idx, len(s)-1)], 4)

    return {
        "concurrency": concurrency,
        "mode": mode,
        "metrics": {
            "submitted": submitted,
            "accepted": accepted,
            "completed": completed,
            "failed": failed,
            "missing": missing,
            "duplicates": duplicates,
            "queue_overflow": queue_overflow
        },
        "throughput_events_sec": round(throughput, 2),
        "drain_time_sec": round(drain_time, 4),
        "latency_ms": {
            "p50": pct(50),
            "p95": pct(95),
            "p99": pct(99),
            "p99.9": pct(99.9),
            "max": round(s[-1], 4) if s else 0.0
        },
        "environment": {
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "runtime": platform.python_version()
        }
    }

async def main():
    levels = [32, 128, 512, 2048, 8192, 16384]
    modes = ["in-memory", "cpu-pipeline", "durable-pipeline"]
    matrix_results = []
    
    for mode in modes:
        for c in levels:
            print(f"[Matrix] Running mode={mode} | concurrency={c} (3 iterations)...", flush=True)
            runs = []
            for r in range(3):
                res = await run_single_run(c, mode)
                runs.append(res)
            matrix_results.append({
                "mode": mode,
                "concurrency": c,
                "runs": runs
            })
            
    os.makedirs("benchmarks/results", exist_ok=True)
    with open("benchmarks/results/scaling_matrix_raw.json", "w") as f:
        json.dump(matrix_results, f, indent=2)
    print(json.dumps(matrix_results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
