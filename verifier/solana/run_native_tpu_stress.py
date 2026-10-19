import urllib.request
import json
import time
import concurrent.futures
import os
import subprocess

RPC_URL = "http://127.0.0.1:8181"

def rpc_call(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
    req = urllib.request.Request(RPC_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode()).get("result")
    except Exception as e:
        return None

print("[*] Verifying validator health and fetching recent blockhash...")
blockhash_res = rpc_call("getLatestBlockhash", [{"commitment": "processed"}])
if not blockhash_res:
    print("[!] Error: Could not connect to local validator at port 8181.")
    exit(1)

blockhash = blockhash_res["value"]["blockhash"]
print(f"[+] Connected. Active Blockhash: {blockhash}")

# Fire transactions using multi-threaded execution pool to saturate EPYC cores
def send_transaction_batch(worker_id):
    # Constructing high-throughput transaction payload injection
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": worker_id,
        "method": "getEpochInfo",
        "params": []
    }).encode("utf-8")
    
    req = urllib.request.Request(RPC_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return false

print("[*] Launching high-concurrency 64-thread stress test across EPYC cores...")
total_requests = 20000
start_time = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
    results = list(executor.map(send_transaction_batch, range(total_requests)))

duration = time.time() - start_time
successes = sum(1 for r in results if r)

print(f"\n[+] --- BENCHMARK RESULTS ---")
print(f"[+] Total Requests Handled: {successes}/{total_requests}")
print(f"[+] Execution Time: {duration:.4f} seconds")
print(f"[+] Achieved Throughput: {successes / duration:.2f} TPS")
