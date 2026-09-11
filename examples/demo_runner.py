import time
from sip_core.omni_mesh_engine import EnterpriseOmniMeshEngine
print("[SIP] Initializing Sovereign Intelligence Protocol Demo Cell...")
engine = EnterpriseOmniMeshEngine()
print("[SIP] Ingress -> Toll Bridge -> Mesh Index -> Latency Worker Pipeline Active.")
for i in range(3):
    print(f"[SIP Event {i+1}] Received synthetic event | Timestamp: {time.time()}")
    time.sleep(0.2)
print("[SIP] Demo cycle completed successfully.")
