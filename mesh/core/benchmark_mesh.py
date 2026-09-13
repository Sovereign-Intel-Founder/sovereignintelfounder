import time
import urllib.request
import urllib.error
import json
import os

# Target your local toll bridge or gateway endpoint
TARGET_URL = "http://localhost:8080/v1/ingress/raw"
ITERATIONS = 1000

results = {
    "timestamp": time.time(),
    "iterations": ITERATIONS,
    "latencies_ms": [],
    "status_codes": {}
}

print(f"Executing Sovereign Intelligence Protocol Benchmark ({ITERATIONS} requests)...")

for _ in range(ITERATIONS):
    start_time = time.perf_counter()
    try:
        req = urllib.request.Request(
            TARGET_URL, 
            headers={"User-Agent": "SIP-Benchmark-Agent/1.0", "X-Harmony-Rhythm": "369"}
        )
        with urllib.request.urlopen(req, timeout=1.0) as response:
            status = response.code
            duration = (time.perf_counter() - start_time) * 1000
            results["latencies_ms"].append(round(duration, 4))
            results["status_codes"][status] = results["status_codes"].get(status, 0) + 1
    except urllib.error.HTTPError as e:
        duration = (time.perf_counter() - start_time) * 1000
        results["latencies_ms"].append(round(duration, 4))
        results["status_codes"][e.code] = results["status_codes"].get(e.code, 0) + 1
    except Exception:
        pass

os.makedirs("benchmarks", exist_ok=True)
report_path = "benchmarks/latency-distribution-2026.json"
with open(report_path, "w") as f:
    json.dump(results, f, indent=2)

if results["latencies_ms"]:
    avg_lat = sum(results["latencies_ms"]) / len(results["latencies_ms"])
    print(f"Benchmark finished. Average Latency: {avg_lat:.3f} ms")
    print(f"Response breakdown: {results['status_codes']}")
    print(f"Artifact saved to {report_path}")
else:
    print("Benchmark completed, but no responses were recorded. Check server status.")
