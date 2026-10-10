import os
import time
import glob

def prune_workers():
    print("[*] Inspecting worker pool for stale or orphaned processes...")
    stale_count = 0
    active_count = 0
    
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmd = f.read().decode('utf-8', errors='ignore').replace('\x00', ' ').strip()
                if any(k in cmd for k in ['bridge', 'daemon', 'cluster', 'worker']):
                    stat = os.stat(f"/proc/{pid}")
                    age = time.time() - stat.st_mtime
                    
                    # If a worker process has been idling without updates for over 2 hours, flag/terminate it
                    if age > 7200 and 'master_cluster.py' not in cmd:
                        print(f"[-] Pruning stale worker PID {pid}: {cmd} (Idle for {int(age)}s)")
                        os.kill(int(pid), 15)
                        stale_count += 1
                    else:
                        print(f"[+] Verified active worker PID {pid}: {cmd}")
                        active_count += 1
        except Exception:
            continue
            
    print(f"\n[+] Pruning complete. Active workers retained: {active_count}, Stale workers terminated: {stale_count}")

if __name__ == "__main__":
    prune_workers()
