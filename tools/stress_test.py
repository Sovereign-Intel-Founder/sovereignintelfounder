import argparse
import concurrent.futures
import hashlib
import hmac
import urllib.request
import time

SECRET_KEY = b"sovereign_intelligence_protocol_secret"

def sign_payload(payload: bytes) -> str:
    return hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()

def send_request(req_id: int, valid_sig: bool):
    url = "http://127.0.0.1:8080/"
    payload = f'{{"event": "telemetry", "seq": {req_id}}}'.encode('utf-8')
    
    if valid_sig:
        sig = sign_payload(payload)
    else:
        sig = "invalid_signature_hash"
        
    headers = {
        "Content-Type": "application/json",
        "X-SIP-Signature": sig,
        "X-Client-ID": f"stress_bot_{req_id % 10:03d}"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return 500

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--ring-size", type=int, default=65536)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--numa-node", type=int, default=0)
    args = parser.parse_args()

    print(f"=== SATURATION TEST: {args.requests} requests, concurrency={args.concurrency} ===")
    start_time = time.perf_counter()
    
    status_counts = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        # 50% valid signed requests, 50% unsigned requests
        futures = [executor.submit(send_request, i, i % 2 == 0) for i in range(args.requests)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            status_counts[res] = status_counts.get(res, 0) + 1

    elapsed = time.perf_counter() - start_time
    print(f"Completed in {elapsed:.3f}s | Status distribution: {status_counts}")

if __name__ == "__main__":
    main()
