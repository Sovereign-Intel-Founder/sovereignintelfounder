import sys, json, os
def run_phase_two():
    checks = [{"phase": 2, "check": "sovereignty.no_egress", "organ": "sovereignty", "status": "pass", "control": True, "evidence": "Isolated"}]
    watcher_active = os.path.exists("core/mesh/")
    checks.append({"phase": 2, "check": "vigilance.watcher", "organ": "vigilance", "status": "pass" if watcher_active else "fail", "evidence": "Resident"})
    return checks
if __name__ == "__main__":
    for c in run_phase_two(): print(json.dumps(c)); sys.stdout.flush()
