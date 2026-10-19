import urllib.request
import concurrent.futures
import time

URL = "http://127.0.0.1:8080/"
NUM_BOTS = 2
REQUESTS_PER_BOT = 10  # Crosses the 8-request free tier limit

def simulate_bot(bot_id):
    client_hex = f"bot_enforce_test_{bot_id:03d}"
    req = urllib.request.Request(URL, headers={"X-Client-Hex": client_hex})
    
    for i in range(REQUESTS_PER_BOT):
        try:
            with urllib.request.urlopen(req) as response:
                status = response.status
                body = response.read().decode().strip()
                print(f"[Bot {bot_id}] Req {i+1} | Status: {status} | Body: {body}")
        except urllib.error.HTTPError as e:
            body = e.read().decode().strip()
            print(f"[Bot {bot_id}] Req {i+1} | Status: {e.code} | Body: {body}")
        except Exception as e:
            print(f"[Bot {bot_id}] Req {i+1} failed: {e}")
        time.sleep(0.05)

def main():
    print(f"=== LAUNCHING 402 ENFORCEMENT SWARM AGAINST {URL} ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_BOTS) as executor:
        executor.map(simulate_bot, range(NUM_BOTS))
    print("=== 402 ENFORCEMENT SWARM COMPLETE ===")

if __name__ == "__main__":
    main()
