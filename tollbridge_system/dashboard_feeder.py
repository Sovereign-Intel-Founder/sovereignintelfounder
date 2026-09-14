import sqlite3
import json
import os
import subprocess

DB_PATH = "tollbridge_system/beast_ultimate_ledger.db"
OUTPUT_JSON = "dashboard_data.json"

def is_process_running(process_name):
    try:
        output = subprocess.check_output(["pgrep", "-f", process_name])
        return len(output.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def get_telemetry():
    if not os.path.exists(DB_PATH):
        return {"status": "error", "message": "Database file not found"}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(component_registry);")
        col_info = cursor.fetchall()
        col_names = [col[1] for col in col_info]
        
        cursor.execute("SELECT * FROM component_registry;")
        rows = cursor.fetchall()
        
        components = []
        active_count = 0
        stopped_count = 0

        for row in rows:
            comp_dict = dict(zip(col_names, row))
            comp_name = comp_dict.get("component_name", "")
            
            if comp_name and is_process_running(comp_name):
                live_status = "ACTIVE"
            else:
                live_status = comp_dict.get("status", "STOPPED")

            if live_status == "ACTIVE":
                active_count += 1
            else:
                stopped_count += 1

            comp_dict["status"] = live_status
            components.append(comp_dict)

        # Fetch recent logs
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        recent_logs = []
        target_table = "telemetry_log" if "telemetry_log" in tables else (tables[0] if tables else None)
        
        if target_table:
            try:
                cursor.execute(f"SELECT * FROM {target_table} ORDER BY ROWID DESC LIMIT 20;")
                recent_logs = [str(r) for r in cursor.fetchall()]
            except Exception:
                pass

        conn.close()

        payload = {
            "status": "success",
            "metrics": {
                "total_components": len(components),
                "active": active_count,
                "stopped": stopped_count
            },
            "components": components,
            "recent_logs": recent_logs
        }
        
        # Write out to static JSON for the UI
        with open(OUTPUT_JSON, "w") as f:
            json.dump(payload, f, indent=2)
            
        return payload
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    get_telemetry()
    print("Telemetry payload written to dashboard_data.json")
