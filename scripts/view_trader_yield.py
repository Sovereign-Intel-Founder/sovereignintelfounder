import sqlite3
import time

DB_PATH = "telemetry.db"

def display_dashboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n========================================================")
    print("      SOVEREIGN INTELLIGENCE PROTOCOL - TRADER YIELD     ")
    print("========================================================")

    cursor.execute("""
        SELECT 
            tier_id, 
            COUNT(packet_id) as pkts, 
            AVG(latency_ns) as avg_lat_ns, 
            SUM(charged_price) as yield
        FROM tollbridge_ingress
        WHERE tier_id IS NOT NULL
        GROUP BY tier_id
    """)
    
    rows = cursor.fetchall()
    if not rows:
        print("No billed packets recorded yet.")
    else:
        print(f"{'TIER ID':<30} | {'PACKETS':<8} | {'AVG LAT (ns)':<12} | {'YIELD ($)':<10}")
        print("-" * 68)
        for tier_id, pkts, avg_lat, yield_val in rows:
            avg_lat_str = f"{avg_lat:.1f}" if avg_lat else "N/A"
            yield_str = f"${yield_val:.4f}" if yield_val else "$0.0000"
            print(f"{tier_id:<30} | {pkts:<8} | {avg_lat_str:<12} | {yield_str:<10}")

    cursor.execute("SELECT COALESCE(SUM(charged_price), 0.0) FROM tollbridge_ingress")
    total = cursor.fetchone()[0]
    print("-" * 68)
    print(f"TOTAL COMPOUNDED REVENUE: ${total:.4f}\n")
    conn.close()

if __name__ == "__main__":
    display_dashboard()
