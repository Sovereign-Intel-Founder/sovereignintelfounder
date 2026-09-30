import os
import json
import sys
import glob

TELEMETRY_DIR = "telemetry"

def audit_file(filepath):
    print(f"Auditing: {filepath}...", end=" ")
    if not os.path.exists(filepath):
        print("[FAIL] File does not exist.")
        return False
    if os.path.getsize(filepath) == 0:
        print("[FAIL] File is completely empty (zero bytes).")
        return False
    if filepath.endswith(".json"):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if not data:
                    print("[FAIL] JSON file is empty or null.")
                    return False
        except json.JSONDecodeError as e:
            print(f"[FAIL] Invalid JSON syntax: {e}")
            return False
    elif filepath.endswith(".log") or filepath.endswith(".csv"):
        with open(filepath, "r", errors="ignore") as f:
            lines = f.readlines()
            if len(lines) == 0:
                print("[FAIL] Log/CSV file contains no lines.")
                return False
    print("[PASS] Verified structural integrity.")
    return True

def main():
    print("=========================================================")
    print("   SOVEREIGN INTELLIGENCE PROTOCOL: PROOF INTEGRITY AUDIT")
    print("=========================================================")
    if not os.path.exists(TELEMETRY_DIR):
        print(f"Error: Directory '{TELEMETRY_DIR}' not found.")
        sys.exit(1)
    all_files = glob.glob(f"{TELEMETRY_DIR}/**/*", recursive=True)
    files_to_check = [f for f in all_files if os.path.isfile(f)]
    passed, failed = 0, 0
    for filepath in sorted(files_to_check):
        if audit_file(filepath):
            passed += 1
        else:
            failed += 1
    print("=========================================================")
    print(f"   AUDIT COMPLETE: Passed: {passed} | Failed/Flagged: {failed}")
    print("=========================================================")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
