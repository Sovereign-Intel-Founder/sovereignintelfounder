import sqlite3
import sys

DB_PATH = "revenue_vault.db"

def show_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM config WHERE key='mode'")
    mode = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), SUM(payload_size), SUM(charged_amount) FROM ledger")
    req_count, total_bytes, total_rev = cursor.fetchone()
    total_bytes = total_bytes or 0
    total_rev = total_rev or 0.0
    
    cursor.execute("SELECT COUNT(DISTINCT client_ip) FROM ledger")
    unique_bots = cursor.fetchone()[0]
    
    print("\n=== Ashburn Node Dashboard ===")
    print(f"Current Operating Mode : {mode.upper()}")
    print(f"Total Requests Handled : {req_count}")
    print(f"Unique Callers (Bots)  : {unique_bots}")
    print(f"Total Data Processed   : {total_bytes} bytes")
    print(f"Total Revenue Generated: ${total_rev:.4f}")
    
    cursor.execute("SELECT client_ip, user_agent, timestamp FROM ledger ORDER BY id DESC LIMIT 5")
    recent = cursor.fetchall()
    print("\n--- Recent Unique Callers ---")
    for ip, ua, ts in recent:
        print(f"IP: {ip} | Agent: {ua} | Last Seen: {int(ts)}")
    print("=============================\n")
    conn.close()

def set_mode(new_mode):
    if new_mode not in ["sandbox", "paid"]:
        print("Error: Mode must be 'sandbox' or 'paid'")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE config SET value=? WHERE key='mode'", (new_mode,))
    conn.commit()
    conn.close()
    print(f"✅ Node operating mode successfully switched to: {new_mode.upper()}")

if __name__ == "__main__":
    if "--status" in sys.argv:
        show_status()
    elif "--set-mode" in sys.argv:
        idx = sys.argv.index("--set-mode")
        if idx + 1 < len(sys.argv):
            set_mode(sys.argv[idx + 1])
        else:
            print("Specify mode: python vault_manager.py --set-mode paid")
    else:
            print("Usage: python vault_manager.py --status OR --set-mode [sandbox|paid]")
