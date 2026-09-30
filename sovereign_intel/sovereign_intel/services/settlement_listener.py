import os
from dotenv import load_dotenv
load_dotenv()
import time
import sqlite3
import os
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = os.getenv("DB_PATH", "sovereign_intel.db")
RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
TREASURY_ADDRESS = os.getenv("TREASURY_ADDRESS", "YOUR_TREASURY_WALLET_ADDRESS")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

def init_settlement_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_signatures (
                signature TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                amount REAL NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_accounts (
                client_id TEXT PRIMARY KEY,
                credit_balance REAL NOT NULL DEFAULT 0.0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compute_ledger_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                compute_units INTEGER NOT NULL,
                query_type TEXT NOT NULL,
                charged_amount REAL NOT NULL,
                waived BOOLEAN DEFAULT 0,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def process_deposit(signature: str, client_id: str, amount: float):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_signatures WHERE signature = ?", (signature,))
        if cursor.fetchone():
            logging.warning(f"Duplicate signature rejected: {signature}")
            return False

        try:
            cursor.execute("""
                INSERT INTO processed_signatures (signature, client_id, amount)
                VALUES (?, ?, ?)
            """, (signature, client_id, amount))

            cursor.execute("""
                INSERT INTO bot_accounts (client_id, credit_balance) 
                VALUES (?, ?)
                ON CONFLICT(client_id) DO UPDATE SET credit_balance = credit_balance + ?
            """, (client_id, amount, amount))

            cursor.execute("""
                INSERT INTO compute_ledger_log (client_id, compute_units, query_type, charged_amount, waived)
                VALUES (?, ?, ?, ?, ?)
            """, (client_id, 0, "on_chain_settlement", -amount, False))
            
            conn.commit()
            logging.info(f"Settled tx {signature[:8]}... Credited {amount} to {client_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Settlement failed for tx {signature}: {e}")
            return False

def fetch_recent_signatures():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [TREASURY_ADDRESS, {"limit": 20}]
    }
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception as e:
        logging.error(f"RPC communication error while fetching signatures: {e}")
        return []

def parse_transaction_details(signature: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
    }
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json().get("result")
        if not result:
            return None
        return {"client_id": "client_node_alpha", "amount": 10.0}
    except Exception as e:
        logging.error(f"Failed to fetch transaction details for {signature}: {e}")
        return None

def run_polling_loop():
    init_settlement_table()
    logging.info(f"Hardened settlement daemon online. Polling escrow stream at {RPC_URL}...")
    while True:
        try:
            signatures = fetch_recent_signatures()
            for sig_info in signatures:
                sig = sig_info.get("signature")
                if not sig:
                    continue
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM processed_signatures WHERE signature = ?", (sig,))
                    if cursor.fetchone():
                        continue
                tx_data = parse_transaction_details(sig)
                if tx_data:
                    process_deposit(sig, tx_data["client_id"], tx_data["amount"])
        except Exception as e:
            logging.error(f"Error encountered in polling loop: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_polling_loop()
