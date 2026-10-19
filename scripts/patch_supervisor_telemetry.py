import sqlite3
import time

DB_PATH = "telemetry.db"

def update_supervisor_telemetry():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Query compounding yield and active billed volume
    cursor.execute("""
        SELECT 
            COUNT(packet_id), 
            COALESCE(SUM(charged_price), 0.0),
            COUNT(DISTINCT tier_id)
        FROM tollbridge_ingress 
        WHERE charged_price IS NOT NULL
    """)
    total_packets, total_yield, active_tiers = cursor.fetchone()

    log_line = f"[ASHBURN-CLUSTER-SUPERVISOR] INFO: Dynamic ledger active. Tiers: {active_tiers}/4 | Billed Packets: {total_packets} | Total Compounded Yield: ${total_yield:.4f}"
    
    print("[+] Updated supervisor telemetry output:")
    print(log_line)
    
    conn.close()

if __name__ == "__main__":
    update_supervisor_telemetry()
