import sqlite3, json, urllib.request
RPC = "http://127.0.0.1:8899"
VAULT = "EwRDhHyksf71qwR4YbXttkBH1NCBwnixeUKQBCWv7"
def get_balance():
    req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc":"2.0","id":1,"method":"getBalance","params":[VAULT]}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode())["result"]["value"] / 1_000_000_000
    except: return 0.0
def fetch_ledger():
    conn = sqlite3.connect("/home/joshua445/sip_core/tollbridge.db")
    val = conn.cursor().execute("SELECT SUM(amount) FROM charges WHERE settled = 0;").fetchone()[0]
    conn.close(); return val if val else 0.0
if __name__ == "__main__":
    print(f"Unsettled Ledger Total: ${fetch_ledger():,.2f}")
    print(f"Private Node Balance: {get_balance():,.4f} SOL")
