import time, json
from concurrent.futures import ThreadPoolExecutor
from solana.rpc.api import Client

client = Client("https://api.mainnet-beta.solana.com")
n = 240
t = 30

def fetch():
    try:
        return client.get_slot()
    except Exception:
        return None

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=t) as ex:
    results = list(ex.map(lambda _: fetch(), range(n)))
dur = time.perf_counter() - start

successes = [r for r in results if r is not None]
print(json.dumps({
    "submitted_total": n,
    "completed": len(successes),
    "threads": t,
    "duration_ms": round(dur * 1000, 2),
    "throughput_events_per_second": round(len(successes) / dur if dur > 0 else 0, 3)
}, indent=2))
