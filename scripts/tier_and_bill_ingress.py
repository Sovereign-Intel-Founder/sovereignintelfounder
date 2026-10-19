import sqlite3
import time

DB_PATH = "telemetry.db"

def process_unpriced_ingress():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Fetch active dynamic prices per tier
    cursor.execute("SELECT tier_id, dynamic_price FROM trader_compute_ledger")
    pricing_map = dict(cursor.fetchall())
    
    if not pricing_map:
        print("[-] Trader compute ledger empty. Please ensure update_ledger_compounding.py ran.")
        conn.close()
        return

    # Select unpriced ingress packets
    cursor.execute("""
        SELECT packet_id, payload, latency_ns 
        FROM tollbridge_ingress 
        WHERE charged_price IS NULL
    """)
    unpriced_packets = cursor.fetchall()

    if not unpriced_packets:
        print("[+] All ingress packets are fully processed and billed.")
        conn.close()
        return

    processed_count = 0
    total_yield = 0.0

    for packet_id, payload, latency_ns in unpriced_packets:
        # Determine tier based on payload content or nanosecond execution speed
        if latency_ns and latency_ns < 1000: # Sub-microsecond
            assigned_tier = "tier_baremetal_isolated_core"
        elif "sim" in str(payload).lower():
            assigned_tier = "tier_predictive_mesh_sim"
        elif latency_ns and latency_ns < 10000:
            assigned_tier = "tier_low_latency_bypass"
        else:
            assigned_tier = "tier_standard_ingress"

        price = pricing_map.get(assigned_tier, 0.001)
        
        # Apply compounding charge
        cursor.execute("""
            UPDATE tollbridge_ingress 
            SET tier_id = ?, charged_price = ? 
            WHERE packet_id = ?
        """, (assigned_tier, price, packet_id))

        processed_count += 1
        total_yield += price

    conn.commit()
    conn.close()
    print(f"[+] Successfully billed {processed_count} packets. Added yield: ${total_yield:.4f}")

if __name__ == "__main__":
    process_unpriced_ingress()
