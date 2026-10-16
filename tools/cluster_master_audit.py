from collections import deque
from datetime import datetime
from pathlib import Path
import re
import subprocess

ROOT = Path("/home/joshua445/sip_hardening")
LIMIT = 10
FLAGS = re.compile(r"\b(ERROR|FATAL|CRITICAL|EXCEPTION|TRACEBACK|FAILED|WARN)\b", re.I)

def show(name, lines, detail):
    print(f"\n=== {name} ===")
    print(detail)
    if not lines:
        print("No entries available.")
        return
    for line in lines:
        print(line.rstrip())
    count = sum(bool(FLAGS.search(line)) for line in lines)
    print(f"Warning/error markers in these {len(lines)} entries: {count}")

def show_file(name, path):
    try:
        with path.open(errors="replace") as f:
            lines = deque(f, maxlen=LIMIT)
        if path.exists():
            changed = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
            detail = f"{path} | last modified: {changed.isoformat(timespec='seconds')}"
        else:
            detail = f"Not found: {path}"
        show(name, lines, detail)
    except FileNotFoundError:
        show(name, [], f"Not found: {path}")
    except OSError as e:
        show(name, [], f"Cannot read {path}: {e}")

show_file("SIP daemon", ROOT / "sip_daemon.log")
show_file("Reported unified log", ROOT / "evidence/straightened_system.log")

try:
    result = subprocess.run(
        ["journalctl", "-u", "sip-master-supervisor.service",
         "-n", str(LIMIT), "--no-pager", "-o", "short-iso"],
        capture_output=True, text=True, timeout=8
    )
    if result.returncode == 0:
        lines = [s for s in result.stdout.splitlines()
                 if s.strip() and s.strip() != "-- No entries --"]
        show("Master supervisor journal", lines,
             "Source: sip-master-supervisor.service")
    else:
        show("Master supervisor journal", [],
             result.stderr.strip() or "Journal query failed.")
except (OSError, subprocess.TimeoutExpired) as e:
    show("Master supervisor journal", [], f"Journal unavailable: {e}")

print("\nCoverage note: this only checks the sources above.")
print("Uncaptured logs cannot be inspected; no entries does not mean healthy.")
