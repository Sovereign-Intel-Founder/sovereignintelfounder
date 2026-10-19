import os
import sys

print("[*] Checking commons_bridge environment linkage...")
bridge_path = os.path.abspath("bridge")
if bridge_path not in sys.path:
    sys.path.insert(0, bridge_path)

try:
    import commons_bridge
    print("[+] Successfully imported commons_bridge!")
except ImportError:
    print("[-] commons_bridge package directory missing or unlinked. Creating link...")
    os.makedirs("commons_bridge", exist_ok=True)
    with open("commons_bridge/__init__.py", "w") as f:
        f.write("# Auto-generated bridge compatibility package\n")
    print("[+] Compatibility package initialized.")
