import os
from pathlib import Path

def straighten_logs():
    input_log = Path('sip_daemon.log')
    output_dir = Path('evidence')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_log = output_dir / 'straightened_system.log'
    
    count = 0
    with open(output_log, 'w', encoding='utf-8', errors='ignore') as out:
        out.write("=== SOVEREIGN SYSTEM AUTOMATED LOG COMPILATION ===\n")
        
        # Process sip_daemon.log if it exists
        daemon_src = Path('sip_daemon.log')
        if daemon_src.exists():
            with open(daemon_src, 'r', encoding='utf-8', errors='ignore') as src:
                for line in src:
                    line_str = line.strip()
                    if line_str:
                        out.write(f"[SIP-DAEMON] {line_str}\n")
                        count += 1
                        
    print(f"[+] Success! Cleaned and compiled {count} log entries into: {output_log}")

if __name__ == '__main__':
    straighten_logs()
