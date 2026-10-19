import json, csv, os

def convert():
    path = "benchmarks/results/scaling_matrix_raw.json"
    if not os.path.exists(path): return
    with open(path, "r") as f: data = json.load(f)
    with open("benchmarks/results/scaling_matrix_plot.csv", "w", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=["mode", "concurrency", "throughput_events_sec", "p50_ms", "p999_ms", "completed"])
        writer.writeheader()
        for entry in data:
            for run in entry["runs"]:
                writer.writerow({
                    "mode": entry["mode"], "concurrency": entry["concurrency"],
                    "throughput_events_sec": run["throughput_events_sec"],
                    "p50_ms": run["latency_ms"]["p50"], "p999_ms": run["latency_ms"]["p99.9"],
                    "completed": run["metrics"]["completed"]
                })

if __name__ == "__main__": convert()
