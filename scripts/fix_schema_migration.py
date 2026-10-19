import sqlite3

DB_PATH = "telemetry.db"

def migrate_schema():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    
    cursor = conn.cursor()
    
    # Check existing columns in tollbridge_ingress
    cursor.execute("PRAGMA table_info(tollbridge_ingress);")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"[-] Existing columns: {columns}")
    
    if "tier_id" not in columns:
        print("[+] Adding tier_id column...")
        cursor.execute("ALTER TABLE tollbridge_ingress ADD COLUMN tier_id TEXT;")
        
    if "charged_price" not in columns:
        print("[+] Adding charged_price column...")
        cursor.execute("ALTER TABLE tollbridge_ingress ADD COLUMN charged_price REAL;")
        
    conn.commit()
    conn.close()
    print("[+] Schema migration completed successfully.")

if __name__ == "__main__":
    migrate_schema()
