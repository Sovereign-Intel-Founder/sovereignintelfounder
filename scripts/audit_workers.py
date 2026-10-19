import os
import time
import glob
import sqlite3

def check_workers():
    print("[*] Auditing worker efficiency and liveness...")
    
    # Check running python processes
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    active_workers = 0
    
    for pid in pids:
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmd = f.read().decode('utf-8', errors='ignore').replace('\x00', ' ').strip()
                if any(k in cmd for k in ['bridge', 'daemon', 'cluster', 'worker']):
                    stat = os.stat(f"/proc/{pid}")
                    uptime = time.time() - stat.st_mtime
                    print(f"  - PID {pid}: {cmd} (Running/Idle for {int(uptime)}s)")
                    active_workers += 1
        except Exception:
            continue
            
    print(f"\n[+] Total active worker/bridge processes detected: {active_workers}")
    
    # Check SQLite WAL shard activity
    shards = glob.glob("databases/sqlite_shards/*.db")
    active_shards = 0
    for shard in shards:
        try:
            mtime = os.path.getmtime(shard)
            if time.time() - mtime < 3600: # Modified in the last hour
                active_shards += 1
        except Exception:
            continue
            
    print(f"[+] Shards with recent write activity (< 1 hour): {active_shards}/{len(shards)}")

if __name__ == "__main__":
    check_workers()
