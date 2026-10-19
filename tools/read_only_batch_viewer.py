import subprocess
from pathlib import Path

def view_combined_logs(limit=50):
    entries = []
    
    # 1. Read sip_daemon.log
    daemon_path = Path('sip_daemon.log')
    if daemon_path.exists():
        with open(daemon_path, 'r', errors='ignore') as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    entries.append(("[SIP-DAEMON]", line_str))
                    
    # 2. Read supervisor systemd journal
    try:
        res = subprocess.run(
            ['journalctl', '-u', 'sip-master-supervisor.service', '-n', str(limit), '--no-pager'],
            capture_output=True, text=True, check=True
        )
        journal_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        if not journal_lines or "-- No entries --" in res.stdout:
            entries.append(("[SUPERVISOR]", "-- No entries -- (Journal is empty for this unit)"))
        else:
            for line in journal_lines:
                entries.append(("[SUPERVISOR]", line))
    except Exception as e:
        entries.append(("[SUPERVISOR]", f"Journal read restricted or unavailable: {e}"))
        
    # Status Header
    print("=== LOG COVERAGE STATUS ===")
    print("[SIP-DAEMON]   : CAPTURED (sip_daemon.log)")
    print("[SUPERVISOR]   : QUERYABLE (Systemd Journal)")
    print("[TOLL-BRIDGE]  : MISSING (Pending persistent capture path)\n")
    
    print(f"=== LATEST COMBINED LOGS (Showing up to {limit} entries) ===")
    for source, text in entries[-limit:]:
        print(f"{source} {text}")

if __name__ == '__main__':
    view_combined_logs(50)
