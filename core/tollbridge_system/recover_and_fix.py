import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
#!/usr/bin/env python3
"""
=============================================================================
MASTER SYSTEM RECOVERY & WORKSPACE SWEEPER
Scans the system for lost scripts, consolidates them into the workspace,
and rebuilds the SQLite database schema.
=============================================================================
"""

import os
import sys
import glob
import shutil
import sqlite3

WORKSPACE = "/home/joshua445/tollbridge_system"
DB_PATH = os.path.join(WORKSPACE, "beast_ultimate_ledger.db")

print("=" * 70)
print(" STARTING MASTER SYSTEM SWEEP AND RECOVERY")
print("=" * 70)

# Ensure workspace exists
os.makedirs(WORKSPACE, exist_ok=True)

# 1. SEARCH FOR MISSING FILES ACROSS THE SYSTEM
search_dirs = ["/home/joshua445", "/tmp", "/root"]
target_files = [
    "bridge.py",
    "gateway_module.py",
    "master_bootstrap.py",
    "deep_swarm_auditor.py",
    "bridge_mesh.py"
]

found_files = {}

for s_dir in search_dirs:
    if os.path.exists(s_dir):
        print(f"[*] Sweeping directory: {s_dir}...")
        for root, dirs, files in os.walk(s_dir):
            for file in files:
                if file in target_files:
                    full_path = os.path.join(root, file)
                    if full_path != os.path.join(WORKSPACE, file):
                        found_files[file] = full_path

print("\n[*] Consolidation Summary:")
for target in target_files:
    dest = os.path.join(WORKSPACE, target)
    if os.path.exists(dest):
        print(f"    [OK] Present in workspace: {target}")
    elif target in found_files:
        src = found_files[target]
        shutil.copy2(src, dest)
        print(f"    [RESTORED] Copied {target} from {src} -> {dest}")
    else:
        print(f"    [MISSING] Could not locate {target} on system.")

# 2. FIX SQLITE DATABASE SCHEMA (CREATE MISSING TABLES)
print("\n[*] Rebuilding SQLite Master Ledger Schema...")
try:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create component registry
    c.execute('''
        CREATE TABLE IF NOT EXISTS component_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_name TEXT UNIQUE,
            file_path TEXT,
            file_hash TEXT,
            status TEXT,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create code history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS code_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            action_type TEXT,
            backup_path TEXT,
            description TEXT
        )
    ''')
    
    # Create missing telemetry_log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS telemetry_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            event_level TEXT,
            message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("    [OK] Database schema verified and locked (telemetry_log active).")
except Exception as e:
    print(f"    [!] Database Repair Error: {e}")

print("\n" + "=" * 70)
print(" RECOVERY COMPLETE - READY TO REBOOT SUPERVISOR")
print("=" * 70)
