import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
#!/usr/bin/env python3
"""
=============================================================================
READ-ONLY SYSTEM INVENTORY AUDITOR
Recursively scans for all Python components across directories without
making any changes to files or system state.
=============================================================================
"""

import os
import time

SEARCH_PATHS = [
    "/home/joshua445",
    "/tmp"
]

print("=" * 85)
print(f"{'FILE PATH':<55} | {'SIZE (KB)':<10} | {'LAST MODIFIED'}")
print("=" * 85)

all_scripts = []

for base_path in SEARCH_PATHS:
    if not os.path.exists(base_path):
        continue
    for root, dirs, files in os.walk(base_path):
        # Skip virtual environments or hidden cache folders to avoid clutter
        if ".git" in root or "__pycache__" in root or "venv" in root or ".local" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    size_kb = stat.st_size / 1024.0
                    mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                    all_scripts.append((full_path, size_kb, mtime))
                except Exception:
                    pass

# Sort alphabetically by file path
all_scripts.sort(key=lambda x: x[0])

for path, size, mtime in all_scripts:
    # Truncate path if too long for display
    display_path = path if len(path) <= 55 else "..." + path[-52:]
    print(f"{display_path:<55} | {size:<10.1f} | {mtime}")

print("=" * 85)
print(f"GRAND TOTAL COMPONENTS FOUND: {len(all_scripts)}")
print("=" * 85)
