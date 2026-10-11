import os
import sys
import asyncio
import importlib

sys.path.append(os.path.abspath("core/mesh"))

# Dynamically import modules to bypass rigid class name mismatches
master_cluster_mod = importlib.import_module("core.mesh.core.master_cluster")
index_mod = importlib.import_module("core.mesh.indexing.index")
toll_bridge_mod = importlib.import_module("core.mesh.bridge.toll_bridge")
omni_engine_mod = importlib.import_module("core.mesh.core.omni_mesh_engine")

ClusterSupervisorDaemon = getattr(master_cluster_mod, "ClusterSupervisorDaemon", None)
CapabilityIndex = getattr(index_mod, "CapabilityIndex", None)
OmniMeshEngine = getattr(omni_engine_mod, "OmniMeshEngine", None)

# Automatically find the bridge/toll class available in the module
bridge_classes = [attr for attr in dir(toll_bridge_mod) if isinstance(getattr(toll_bridge_mod, attr), type)]
TollBridgeClass = getattr(toll_bridge_mod, bridge_classes[0], None) if bridge_classes else None

async def main():
    print("\n" + "="*50)
    print("LAUNCHING SOVEREIGN MESH PRODUCTION DAEMON (DYNAMIC)")
    print("="*50)

    cluster = ClusterSupervisorDaemon(cluster_id="ashburn-primary-cluster") if ClusterSupervisorDaemon else None
    index = CapabilityIndex() if CapabilityIndex else None
    toll_bridge = TollBridgeClass() if TollBridgeClass else None
    
    mesh_engine = OmniMeshEngine(gateway_url="http://127.0.0.1:8080/v1/ingress/raw") if OmniMeshEngine else None
    print("[DAEMON] Starting background concurrency workers...")
    
    if mesh_engine:
        engine_task = asyncio.create_task(mesh_engine.start_engine(concurrency_workers=8))
        print("[DAEMON] Cluster live and monitoring. Press Ctrl+C to stop.")
        print("="*50 + "\n")
        await asyncio.gather(engine_task)
    else:
        print("[ERROR] OmniMeshEngine could not be initialized.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Master daemon stopped gracefully.")
