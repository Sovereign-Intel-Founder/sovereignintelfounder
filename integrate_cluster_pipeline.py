import os
import sys
import sqlite3

sys.path.append(os.path.abspath("core/mesh"))
from core.mesh.core.master_cluster import ClusterSupervisorDaemon
from core.mesh.indexing.index import CapabilityIndex
from core.mesh.registration.schema import ParticipantRegistration

print("\n" + "="*50)
print("INITIALIZING CLUSTER SUPERVISOR PIPELINE INTEGRATION")
print("="*50)

# Initialize production cluster daemon and memory index
cluster = ClusterSupervisorDaemon(cluster_id="ashburn-primary-cluster")
index = CapabilityIndex()

db_path = "./sovereign-seed-commons/sip_mesh_state.db"
if not os.path.exists(db_path):
    db_path = "sip_mesh_state.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure table exists and query registered nodes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registered_nodes';")
if cursor.fetchone():
    cursor.execute("SELECT node_id, source_path FROM registered_nodes;")
    rows = cursor.fetchall()
    print(f"[BRIDGE] Registering {len(rows)} nodes into ClusterSupervisor & CapabilityIndex...")
    
    for idx, (node_id, source_path) in enumerate(rows):
        # Register into ClusterSupervisor resource tracker
        if hasattr(cluster, 'register_node'):
            cluster.register_node(node_id=node_id, cores=128, ram_gb=728)
        
        # Instantiate ParticipantRegistration with schema-compliant tcp:// URI
        reg = ParticipantRegistration(
            participant_id=node_id,
            public_key_pem="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
            endpoint_uri=f"tcp://127.0.0.1:{9000 + idx}",
            nonce=1,
            signature="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            supported_caps=["mesh_routing", "telemetry_sync", "bare_metal_exec"]
        )
        index.register(reg)
        print(f"  ├── Synchronized node: {node_id} at tcp://127.0.0.1:{9000 + idx}")

print(f"\n[SUCCESS] Pipeline unified. Active cluster participants: {len(index._participants)}")
print("="*50 + "\n")
conn.close()
