import sqlite3
import time

DB_PATH = "telemetry.db"

def run_test():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    # Insert mock incoming packets with varying nanosecond latencies and payloads
    test_packets = [
        ("pkt_test_001", "Standard order payload", 15000, None, None),
        ("pkt_test_002", "High-frequency arbitrage stream", 450, None, None),
        ("pkt_test_003", "Predictive simulation run order-flow", 2500, None, None),
        ("pkt_test_004", "Bare-metal isolated core pipeline packet", 120, None, None)
    ]
    
    for pkt in test_packets:
        cursor.execute("""
            INSERT OR REPLACE INTO tollbridge_ingress 
            (packet_id, payload, latency_ns, tier_id, charged_price, received_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pkt[0], pkt[1], pkt[2], pkt[3], pkt[4], time.time()))
        
    conn.commit()
    conn.close()
    print("[+] Test packets injected into tollbridge_ingress.")

if __name__ == "__main__":
    run_test()
