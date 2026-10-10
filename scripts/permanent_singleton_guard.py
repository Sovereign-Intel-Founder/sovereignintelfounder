import os
import sys
import fcntl
import socket

LOCK_FILE = "/tmp/sovereign_master.lock"

def enforce_singleton():
    lock_fd = open(LOCK_FILE, "w")
    try:
        # Non-blocking exclusive lock check
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("[!] ERROR: Another instance of the Unified Master is already running. Exiting to prevent duplication.")
        sys.exit(1)
        
    print("[+] Singleton lock acquired. Enforcing strict single-process execution.")
    return lock_fd

if __name__ == "__main__":
    fd = enforce_singleton()
    # Keep alive or launch master daemon logic here
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down singleton daemon.")
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()
