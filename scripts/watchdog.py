import os, requests
URL = os.getenv("SIP_WATCHDOG_ENDPOINT", "http://localhost:8080/v1/health")
MUTATION = os.getenv("SIP_ENABLE_MUTATION_TESTS", "false").lower() == "true"
def run():
    print(f"[*] Checking health: {URL}")
    r = requests.get(URL, timeout=5.0)
    assert r.status_code == 200, f"Failed: {r.status_code}"
    print("[+] Health check passed (Read-Only).")
    if MUTATION:
        print("[!] Executing mutation POST...")
        requests.post(f"{URL}/canary", json={"test": True}, timeout=5.0)
if __name__ == "__main__": run()
