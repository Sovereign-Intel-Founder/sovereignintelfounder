import os
import sys
import sqlite3
import importlib.util

print("\n" + "="*60)
print("SOVEREIGN MESH PIPELINE & WIRING AUDIT")
print("="*60)

# 1. Check Database Persistence & Tables
db_path = "sip_mesh_state.db"
if not os.path.exists(db_path):
    # Check inside subdirectories if needed
    for root, dirs, files in os.walk('.'):
        if "sip_mesh_state.db" in files:
            db_path = os.path.join(root, "sip_mesh_state.db")
            break

print(f"\n[1] DATABASE STATUS:")
if os.path.exists(db_path):
    print(f"  ├── Found state database at: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"  ├── Active Tables: {tables}")
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t};")
            print(f"  │     └── Table '{t}' row count: {cursor.fetchone()[0]}")
        conn.close()
    except Exception as e:
        print(f"  └── Database read error: {e}")
else:
    print(f"  └── WARNING: No state database found.")

# 2. Verify Module Imports & Core Wiring
print(f"\n[2] MODULE WIRING CHECK:")
sys.path.append(os.path.abspath("core/mesh"))
sys.path.append(os.path.abspath("core/mesh/indexing"))
sys.path.append(os.path.abspath("core/mesh/registration"))

modules_to_check = [
    ("core.mesh.indexing.index", "CapabilityIndex"),
    ("core.mesh.registration.schema", "ParticipantRegistration"),
]

for mod_name, cls_name in modules_to_check:
    try:
        parts = mod_name.split('.')
        mod = __import__(mod_name, fromlist=[cls_name])
        cls = getattr(mod, cls_name)
        print(f"  ├── Successfully loaded: {mod_name}.{cls_name}")
    except Exception as e:
        print(f"  └── WIRING ERROR: Failed to load {mod_name}.{cls_name} -> {e}")

# 3. Check Active Cell/Node Directories on Disk
print(f"\n[3] DISK NODE & CLONE TOPOLOGY:")
cell_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and ('cell' in d or 'commons' in d)]
print(f"  ├── Found matching local node/cell paths: {len(cell_dirs)}")
for d in sorted(cell_dirs):
    print(f"  │     └── {d}")

print("\n" + "="*60)
print("AUDIT COMPLETE. Review any wiring gaps above.")
print("="*60 + "\n")
