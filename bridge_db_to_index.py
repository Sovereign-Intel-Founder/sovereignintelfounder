import sqlite3
import sys
import os

sys.path.append(os.path.abspath("core/mesh"))
from core.mesh.indexing.index import CapabilityIndex
from core.mesh.registration.schema import ParticipantRegistration

db_path = "./sovereign-seed-commons/sip_mesh_state.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

index = CapabilityIndex()

# Pull registered nodes and load into memory index
try:
    cursor.execute("SELECT node_id, source_path, status FROM registered_nodes;")
    rows = cursor.fetchall()
    print(f"[BRIDGE] Loading {len(rows)} nodes from SQLite into CapabilityIndex...")
    for row in rows:
        node_id, source_path, status = row
        # Construct registration stub with default capabilities for active routing
        reg = ParticipantRegistration(
            participant_id=node_id,
            supported_caps=["mesh_routing", "telemetry_sync"]
        )
        index.register(reg)
        print(f"  ├── Registered into memory: {node_id}")
        
    print(f"\n[SUCCESS] CapabilityIndex successfully synchronized. Total active participants: {len(index._participants)}")
except Exception as e:
    print(f"[BRIDGE ERROR] Failed to sync index: {e}")
finally:
    conn.close()
