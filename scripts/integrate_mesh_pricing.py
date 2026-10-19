import re

file_path = "toll_bridge_daemon.py"

with open(file_path, "r") as f:
    content = f.read()

# Unified Mesh + Dynamic Tiered Pricing Ingress Hook
mesh_pricing_hook = """
        # --- SOVEREIGN INTELLIGENCE PROTOCOL: MESH & PRICING INTEGRATION ---
        import sqlite3
        import time

        packet_id = f"pkt_mesh_{int(time.time_ns())}"
        latency_ns = int((time.perf_counter() - start_time) * 1e9)

        # Dynamic multi-tier pricing scaling from micro-charges to elite execution fees
        if latency_ns < 200:
            tier_id = "tier_baremetal_isolated_core"
            charged_price = 1440.00
            node_tier = "baremetal-128core"
        elif latency_ns < 1000:
            tier_id = "tier_low_latency_bypass"
            charged_price = 360.00
            node_tier = "kernel-bypass"
        elif latency_ns < 5000:
            tier_id = "tier_predictive_mesh_sim"
            charged_price = 45.568
            node_tier = "mesh-sim"
        else:
            tier_id = "tier_standard_ingress"
            charged_price = 0.0010
            node_tier = "free-tier"

        try:
            conn = sqlite3.connect("telemetry.db")
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO tollbridge_ingress 
                (packet_id, payload, latency_ns, tier_id, charged_price, received_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (packet_id, f"{method} {path} [Mesh-Grid-Active]", latency_ns, tier_id, charged_price, time.time()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[!] Mesh SQLite WAL Write Error: {e}")
        # -----------------------------------------------------------------
"""

# Replace or insert right before response handling
if "content_length = 0" in content:
    new_content = content.replace("content_length = 0", "content_length = 0\n" + mesh_pricing_hook)
    with open(file_path, "w") as f:
        f.write(new_content)
    print("[+] Successfully integrated Mesh and Tiered Pricing directly into toll_bridge_daemon.py")
else:
    print("[!] Target anchor not found.")
