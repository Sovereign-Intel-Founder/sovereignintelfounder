import subprocess
import time
import sqlite3

DB_PATH = "telemetry.db"
LOG_PATH = "toll_bridge.log"

def production_loop():
    print("[+] Starting Sovereign Intelligence Protocol Master Production Loop...")
    
    while True:
        try:
            # Step 1: Run real-time billing and tier assignment on new ingress
            subprocess.run(["python3", "tier_and_bill_ingress.py"], check=True)
            
            # Step 2: Append live supervisor heartbeat to log
            subprocess.run(["python3", "integrate_supervisor_yield.py"], check=True)
            
            # Pulse interval for live engine tracking
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n[-] Shutting down production engine safely.")
            break
        except Exception as e:
            print(f"[!] Error in supervisor loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    production_loop()
