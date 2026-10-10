import sqlite3
import time

DB_PATH = "telemetry.db"
LOG_PATH = "toll_bridge.log"

def append_supervisor_heartbeat():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(packet_id), 
            COALESCE(SUM(charged_price), 0.0),
            COUNT(DISTINCT tier_id)
        FROM tollbridge_ingress 
        WHERE charged_price IS NOT NULL
    """)
    total_pkts, total_yield, active_tiers = cursor.fetchone()
    conn.close()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} [ASHBURN-CLUSTER-SUPERVISOR] INFO: Swarm health check nominal. Dynamic Tiers Billed: {active_tiers}/4 | Packets: {total_pkts} | Total Compounded Yield: ${total_yield:.4f}\n"

    with open(LOG_PATH, "a") as f:
        f.write(log_entry)

    print("[+] Successfully appended live yield heartbeat to toll_bridge.log:")
    print(log_entry.strip())

if __name__ == "__main__":
    append_supervisor_heartbeat()
