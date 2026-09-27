#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

FRAMEWORK = Path('/opt/tollbridge_system/tollbridge_backend_framework.py')
CONFIG = Path('/opt/tollbridge_system/tollbridge_framework.json')
DB = Path('/tmp/tollbridge_concurrency_test.db')
THREADS = 30
EVENTS_PER_THREAD = 8

sys.path.insert(0, str(FRAMEWORK.parent))
import tollbridge_backend_framework as tb  # noqa: E402


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def main() -> int:
    if DB.exists():
        DB.unlink()
    cfg = tb.load_config(CONFIG, DB)
    backend = tb.Backend(cfg)
    runner = threading.Thread(target=backend.run, name='benchmark-dispatcher', daemon=True)
    runner.start()
    barrier = threading.Barrier(THREADS)
    submit_latencies: list[float] = []
    results: list[dict] = []
    lock = threading.Lock()
    start = time.perf_counter()

    def virtual_user(user_id: int) -> None:
        barrier.wait()
        local_results = []
        for seq in range(EVENTS_PER_THREAD):
            event = {
                'operation': 'ingest' if seq % 2 else 'telemetry',
                'event_id': f'concurrency-{user_id}-{seq}',
                'source': f'virtual-user-{user_id}',
                'payload': {'sequence': seq, 'synthetic': True},
            }
            t0 = time.perf_counter()
            response = backend.submit(event)
            elapsed = (time.perf_counter() - t0) * 1000
            local_results.append(response)
            with lock:
                submit_latencies.append(elapsed)
        with lock:
            results.extend(local_results)

    with ThreadPoolExecutor(max_workers=THREADS, thread_name_prefix='virtual-user') as pool:
        futures = [pool.submit(virtual_user, i) for i in range(THREADS)]
        for future in as_completed(futures):
            future.result()
    submit_done = time.perf_counter()
    backend.work.join()
    completion_deadline = time.perf_counter() + 30.0
    while time.perf_counter() < completion_deadline:
        with backend.metrics._lock:
            finished = backend.metrics.completed + backend.metrics.failed
        if finished >= THREADS * EVENTS_PER_THREAD:
            break
        time.sleep(0.005)
    complete_done = time.perf_counter()
    snapshot = backend.metrics.snapshot(backend.work.qsize(), cfg, backend.state)
    backend.shutdown()

    accepted = sum(1 for r in results if r.get('ok'))
    rejected = len(results) - accepted
    total = len(results)
    wal_mode = None
    synchronous = None
    conn = None
    try:
        import sqlite3
        conn = sqlite3.connect(DB)
        wal_mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
        synchronous = conn.execute('PRAGMA synchronous').fetchone()[0]
    finally:
        if conn:
            conn.close()

    report = {
        'threads': THREADS,
        'events_per_thread': EVENTS_PER_THREAD,
        'submitted_total': total,
        'accepted': accepted,
        'rejected': rejected,
        'submit_window_ms': round((submit_done - start) * 1000, 3),
        'drain_window_ms': round((complete_done - submit_done) * 1000, 3),
        'end_to_end_window_ms': round((complete_done - start) * 1000, 3),
        'throughput_events_per_second': round(accepted / max(complete_done - start, 1e-9), 3),
        'submit_latency_ms': {
            'min': round(min(submit_latencies), 3) if submit_latencies else 0.0,
            'p50': round(percentile(submit_latencies, 0.50), 3),
            'p95': round(percentile(submit_latencies, 0.95), 3),
            'p99': round(percentile(submit_latencies, 0.99), 3),
            'max': round(max(submit_latencies), 3) if submit_latencies else 0.0,
            'mean': round(statistics.mean(submit_latencies), 3) if submit_latencies else 0.0,
        },
        'framework_metrics': snapshot,
        'sqlite': {
            'path': str(DB),
            'journal_mode': wal_mode,
            'synchronous_pragma_value': synchronous,
            'file_bytes': DB.stat().st_size,
        },
        'safety': {
            'used_live_ledger': False,
            'used_live_redis': False,
            'used_wallet_or_broadcast': False,
            'synthetic_payloads_only': True,
        },
    }
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
