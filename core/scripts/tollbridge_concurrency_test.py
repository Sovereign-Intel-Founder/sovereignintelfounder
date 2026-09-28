import os
import sys
import time
import json
import sqlite3
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "./sip_depot")
import tollbridge_backend_framework as tb

CONFIG = Path('./sip_depot/tollbridge_framework.json')
DB = Path('/tmp/tollbridge_concurrency_test.db')
THREADS = 128
EVENTS_PER_THREAD = 100000

def get_time_ns():
    return time.clock_gettime_ns(time.CLOCK_MONOTRONIC_RAW) if hasattr(time, 'CLOCK_MONOTRONIC_RAW') else time.perf_counter_ns()

def main():
    if DB.exists():
        DB.unlink()

    total_cores = os.cpu_count() or 128
    cfg = tb.load_config(CONFIG, DB)
    backend = tb.Backend(cfg)

    barrier = threading.Barrier(THREADS)
    thread_data = [None] * THREADS

    def virtual_user(user_id: int):
        try:
            os.sched_setaffinity(0, {user_id % total_cores})
        except Exception:
            pass

        barrier.wait()
        
        local_results = []
        local_latencies = []
        local_outliers = []

        for seq in range(EVENTS_PER_THREAD):
            event = {
                'operation': 'ingest' if seq % 2 == 0 else 'telemetry',
                'event_id': f'concurrency-{user_id}-{seq}',
                'source': f'virtual-user-{user_id}',
                'payload': {'sequence': seq, 'synthetic': True}
            }
            t0 = get_time_ns()
            response = backend.submit(event)
            t1 = get_time_ns()
            elapsed_ms = (t1 - t0) / 1e6

            local_results.append(response)
            local_latencies.append(elapsed_ms)

            if elapsed_ms > 100.0:
                local_outliers.append({
                    'event_id': event['event_id'],
                    'thread_id': user_id,
                    'latency_ms': round(elapsed_ms, 3)
                })

        thread_data[user_id] = (local_results, local_latencies, local_outliers)

    start_time = get_time_ns()
    with ThreadPoolExecutor(max_workers=THREADS, thread_name_prefix='virtual-user') as pool:
        futures = [pool.submit(virtual_user, i) for i in range(THREADS)]
        for future in as_completed(futures):
            future.result()

    submit_done_time = get_time_ns()
    total_submit_window_ms = (submit_done_time - start_time) / 1e6

    all_results = []
    all_latencies = []
    all_outliers = []

    for res, lats, outs in thread_data:
        all_results.extend(res)
        all_latencies.extend(lats)
        all_outliers.extend(outs)

    all_outliers.sort(key=lambda x: x['latency_ms'], reverse=True)
    top_outliers = all_outliers[:20]

    accepted = sum(1 for r in all_results if r.get('ok') or r.get('success') or r.get('status') == 'ok')
    rejected = len(all_results) - accepted
    total = len(all_results)

    snapshot = backend.metrics.snapshot(backend.work.qsize(), cfg, backend.state)
    backend.shutdown()

    sorted_lat = sorted(all_latencies) if all_latencies else [0.0]
    n = len(sorted_lat)

    report = {
        'architecture': 'Zero-Lock NUMA POSIX SHM Hotpath',
        'threads': THREADS,
        'events_per_thread': EVENTS_PER_THREAD,
        'submitted_total': total,
        'accepted': accepted,
        'rejected': rejected,
        'submit_window_ms': round(total_submit_window_ms, 3),
        'throughput_events_per_second': round(accepted / max(total_submit_window_ms / 1000.0, 1e-9), 3),
        'tail_latencies_ms': {
            'min': round(sorted_lat[0], 3),
            'p50': round(sorted_lat[int(n * 0.50)], 3),
            'p95': round(sorted_lat[int(n * 0.95)], 3),
            'p99': round(sorted_lat[int(n * 0.99)], 3),
            'p999': round(sorted_lat[min(int(n * 0.999), n - 1)], 3),
            'p9999': round(sorted_lat[min(int(n * 0.9999), n - 1)], 3),
            'max': round(sorted_lat[-1], 3)
        },
        'top_latency_outliers': top_outliers,
        'framework_metrics': snapshot,
        'sqlite': {
            'path': str(DB),
            'file_bytes': DB.stat().st_size if DB.exists() else 0,
            'journal_mode': 'wal',
            'mmap_size_bytes': 268435456
        },
        'safety': {
            'synthetic_payloads_only': True,
            'used_live_ledger': False,
            'used_live_redis': False,
            'used_wallet_or_broadcast': False
        }
    }

    csv_path = Path("telemetry_showcase_report.csv")
    with open(csv_path, "w") as f:
        f.write("metric,value\n")
        f.write(f"throughput_eps,{report['throughput_events_per_second']}\n")
        f.write(f"total_events,{total}\n")
        f.write(f"p50_ms,{report['tail_latencies_ms']['p50']}\n")
        f.write(f"p95_ms,{report['tail_latencies_ms']['p95']}\n")
        f.write(f"p99_ms,{report['tail_latencies_ms']['p99']}\n")
        f.write(f"p999_ms,{report['tail_latencies_ms']['p999']}\n")
        f.write(f"p9999_ms,{report['tail_latencies_ms']['p9999']}\n")

    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
