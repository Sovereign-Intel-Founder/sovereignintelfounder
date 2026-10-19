import subprocess
from pathlib import Path

def view_logs(batch_size=50):
    print(f"=== SOVEREIGN BATCH LOG VIEWER (Last {batch_size} entries) ===")
    logs = []
    
    # Read sip_daemon.log
    daemon_log = Path('sip_daemon.log')
    if daemon_log.exists():
        with open(daemon_log, 'r', errors='ignore') as f:
            for line in f:
                logs.append(("[SIP-DAEMON]", line.strip()))
                
    # Read systemd journal for master supervisor
    try:
        res = subprocess.run(
            ['journalctl', '-u', 'sip-master-supervisor.service', '-n', str(batch_size), '--no-pager'],
            capture_output=True, text=True, check=True
        )
        for line in res.stdout.splitlines():
            if line.strip():
                logs.append(("[SUPERVISOR]", line.strip()))
    except Exception as e:
        logs.append(("[SUPERVISOR]", f"Journal read restricted: {e}"))
        
    # Display latest batch
    for source, text in logs[-batch_size:]:
        print(f"{source} {text}")

if __name__ == '__main__':
    view_logs(50)
