import urllib.request, json, time, concurrent.futures

url = "http://127.0.0.1:8181"
payload = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getAccountInfo",
    "params": ["8JfDJub5yCu9aXMizfcwPJtnHx1mZxowXE3JtuL1GVvt", {"encoding": "jsonParsed"}]
}).encode("utf-8")

def fire_request(_):
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False

print("[*] Launching 1,000 concurrent verification requests across EPYC threads...")
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
    results = list(executor.map(fire_request, range(1000)))
duration = time.time() - start

successes = sum(1 for r in results if r)
print(f"[+] Completed: {successes}/1000 requests successful")
print(f"[+] Total Time: {duration:.4f}s")
print(f"[+] Throughput: {successes / duration:.2f} req/sec")
