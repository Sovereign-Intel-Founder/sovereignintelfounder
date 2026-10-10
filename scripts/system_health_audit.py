import os

def audit():
    print("[*] Running final system audit...")
    
    paths_to_check = [
        "unified_master_daemon.py",
        "production_lock.json",
        "telemetry.db",
        "test_remote_handoff.py"
    ]
    
    for p in paths_to_check:
        exists = os.path.exists(p)
        print(f"[{'x' if exists else ' '}] {p}: {'Present' if exists else 'Missing'}")

if __name__ == "__main__":
    audit()
