import time
import requests
from datetime import datetime

TARGET_URL = "https://detective-standard-airplane-mountains.trycloudflare.com/v1/ingress"
LOG_FILE = "/home/joshua445/sovereign-intelligence/outage_recovery.log"

def log_event(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    entry = f"[{timestamp}] {message}\n"
    print(entry.strip())
    with open(LOG_FILE, "a") as f:
        f.write(entry)

if __name__ == "__main__":
    log_event("SIP Watchdog Monitor initialized.")
    while True:
        try:
            get_res = requests.get(TARGET_URL, timeout=5)
            get_status = get_res.status_code
        except Exception as e:
            get_status = f"ERROR: {e}"

        canary_payload = {"event_id": f"canary_{int(time.time())}", "actor_role": "watchdog_probe"}
        try:
            post_res = requests.post(TARGET_URL, json=canary_payload, timeout=5)
            post_status = post_res.status_code
        except Exception as e:
            post_status = f"ERROR: {e}"

        failed = False
        if isinstance(get_status, str) or get_status >= 500:
            failed = True
        if isinstance(post_status, str) or post_status >= 500:
            failed = True

        if failed:
            log_event(f"OUTAGE DETECTED! GET Status: {get_status} | POST Status: {post_status}")

        time.sleep(45)
