#!/usr/bin/env python3
"""Read-only SIP workspace and runtime review.

This script inventories only the explicitly selected project roots, matching
processes, matching systemd units, listening sockets, and discovered log files.
It never starts/stops/restarts processes, sends network requests, edits files,
changes permissions, or writes a report. It uses Python's standard library
plus read-only Linux tools when available.

A running process/listener is not proof of functional health. Log keyword
counts are clues, not a correctness test. Run from the server you want to
inspect, preferably as the project owner; use sudo only if needed for access
and if authorized.
"""

from __future__ import annotations

import argparse
import ast
import collections
import datetime as dt
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "1.0"
DEFAULT_UNIT = "sip-master-supervisor.service"
DEFAULT_WORKSPACES = ("sip_hardening", "sovereign_workspace")
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
    "target", "dist", "build", "__pycache__", ".cache", ".rustup",
    "site-packages", "vendor", "coverage", ".tox", ".mypy_cache",
}
PROCESS_MARKERS = (
    "sip", "sovereign", "toll_bridge", "toll-bridge", "ingress",
    "cloudflared", "solana-validator", "uvicorn",
)
KNOWN_LOG_NAMES = (
    "sip_daemon.log",
    "sovereign_master.log",
    "straightened_system.log",
    "live_benchmark_audit.json",
)
LOG_SUFFIXES = (".log", ".out", ".err", ".jsonl")
TEXT_SUFFIXES = {
    ".py", ".c", ".h", ".cc", ".cpp", ".md", ".yml", ".yaml",
    ".json", ".sh", ".toml", ".ini", ".service", ".conf",
}
ERROR_RE = re.compile(
    r"\b(error|fatal|critical|exception|traceback|failed|failure)\b", re.I
)
WARN_RE = re.compile(r"\b(warn|warning|retry|restarting|timeout)\b", re.I)
SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*([^\s,;]+)"), r"\1=[REDACTED]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b"), "[REDACTED_STRIPE_KEY]"),
    (re.compile(r"https?://[^\s/@:]+:[^\s/@]+@" ), "https://[REDACTED]@" ),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY_MARKER]"),
]
TIMESTAMP_RE = re.compile(
    r"(?P<stamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
)


def redact(text: str) -> str:
    """Mask common credential patterns before displaying command/log text."""
    result = text
    for pattern, replacement in SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def short(text: str, limit: int = 260) -> str:
    text = redact(" ".join(text.split()))
    return text if len(text) <= limit else text[: limit - 3] + "..."


def run_command(args: Sequence[str], timeout: int = 5) -> Tuple[int, str, str]:
    """Run a read-only inspection command without a shell."""
    try:
        env = os.environ.copy()
        env["GIT_OPTIONAL_LOCKS"] = "0"
        proc = subprocess.run(
            list(args), capture_output=True, text=True, timeout=timeout,
            check=False, env=env,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"command not installed: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s: {args[0]}"
    except OSError as exc:
        return 126, "", f"could not run {args[0]}: {exc}"


def get_user_home() -> Path:
    """Resolve the invoking user's home even when launched through sudo."""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            pass
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except KeyError:
        return Path.home()


def default_roots() -> List[Path]:
    home = get_user_home()
    roots: List[Path] = []
    for name in DEFAULT_WORKSPACES:
        p = home / name
        if p.exists():
            roots.append(p.resolve())
    cwd = Path.cwd().resolve()
    if cwd.exists() and any((cwd / marker).exists() for marker in (".git", "sip_daemon.c", "sip_master_supervisor.py")):
        roots.append(cwd)
    # Deduplicate while preserving order.
    unique: List[Path] = []
    seen = set()
    for root in roots:
        if str(root) not in seen:
            unique.append(root)
            seen.add(str(root))
    return unique


def print_header(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def bytes_human(n: int) -> str:
    value = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{n} B"


def file_age(path: Path) -> str:
    try:
        seconds = max(0.0, time.time() - path.stat().st_mtime)
        if seconds < 3600:
            return f"{int(seconds // 60)}m ago"
        if seconds < 86400:
            return f"{seconds / 3600:.1f}h ago"
        return f"{seconds / 86400:.1f}d ago"
    except OSError:
        return "unknown age"


def walk_project(root: Path, max_files: int = 25000) -> Tuple[List[Path], bool]:
    """Walk a project without following symlinks or entering dependency/build trees."""
    found: List[Path] = []
    truncated = False
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            path = Path(base) / filename
            try:
                if path.is_symlink():
                    continue
            except OSError:
                continue
            found.append(path)
            if len(found) >= max_files:
                truncated = True
                return found, truncated
    return found, truncated


def git_summary(root: Path) -> None:
    code, out, _ = run_command(["git", "-C", str(root), "rev-parse", "--show-toplevel"])
    if code != 0:
        print("  Git: not a repository root (or git unavailable)")
        return
    top = out.strip()
    code, branch, _ = run_command(["git", "-C", str(root), "status", "--short", "--branch", "--untracked-files=no"])
    code2, commit, _ = run_command(["git", "-C", str(root), "log", "-1", "--format=%h | %cI | %s"])
    print(f"  Git root: {top}")
    if code == 0:
        rows = [line for line in branch.splitlines() if line.strip()]
        print(f"  Git status: {short(rows[0], 180) if rows else 'clean/empty status'}")
        changed = sum(1 for line in rows[1:] if line.strip())
        if changed:
            print(f"  Tracked changed paths: {changed} (untracked paths intentionally omitted)")
    else:
        print("  Git status: unavailable")
    if code2 == 0 and commit.strip():
        print(f"  Latest commit: {short(commit.strip(), 220)}")


def inventory_roots(roots: Sequence[Path], last: int) -> List[Path]:
    all_files: List[Path] = []
    for root in roots:
        print_header(f"WORKSPACE INVENTORY: {root}")
        if not root.exists() or not root.is_dir():
            print("  Root missing or not a directory.")
            continue
        git_summary(root)
        files, truncated = walk_project(root)
        all_files.extend(files)
        ext_counts = collections.Counter(p.suffix.lower() or "[no extension]" for p in files)
        total_bytes = 0
        largest: List[Tuple[int, Path]] = []
        for path in files:
            try:
                size = path.stat().st_size
                total_bytes += size
                largest.append((size, path))
            except OSError:
                continue
        print(f"  Files scanned: {len(files)}" + (" (scan limit reached)" if truncated else ""))
        print(f"  Approximate file bytes (excluding skipped folders): {bytes_human(total_bytes)}")
        print("  File types: " + ", ".join(f"{ext}={count}" for ext, count in ext_counts.most_common(12)))
        print("  Largest files:")
        for size, path in sorted(largest, reverse=True)[:10]:
            print(f"    {bytes_human(size):>10}  {path.relative_to(root)}")
        # Report recency, never declare files stale from timestamps alone.
        recent = sorted(files, key=lambda p: safe_mtime(p), reverse=True)[:last]
        print(f"  {last} most recently modified paths (recency only; not proof of use):")
        for path in recent:
            print(f"    {file_age(path):>10}  {path.relative_to(root)}")
    return all_files


def safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def inspect_manifests(files: Sequence[Path], last: int) -> None:
    candidates = [p for p in files if "manifest" in p.name.lower() and p.suffix.lower() == ".json"]
    print_header("MANIFESTS (STRUCTURE ONLY)")
    if not candidates:
        print("No manifest-named JSON files found in the selected roots.")
        return
    for path in candidates[:last]:
        print(f"  {path}")
        try:
            if path.stat().st_size > 2_000_000:
                print("    Skipped: larger than 2 MB.")
                continue
            data = json.loads(path.read_text(errors="replace"))
            if isinstance(data, dict):
                print(f"    Top-level keys: {', '.join(map(str, list(data.keys())[:30])) or '(none)'}")
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"    {key}: list with {len(value)} item(s)")
                    elif isinstance(value, dict):
                        print(f"    {key}: object with {len(value)} key(s)")
            elif isinstance(data, list):
                print(f"    Top-level JSON list: {len(data)} item(s)")
            else:
                print(f"    Top-level JSON type: {type(data).__name__}")
        except Exception as exc:
            print(f"    Parse error: {type(exc).__name__}: {exc}")


def inspect_python_syntax(files: Sequence[Path], limit: int = 1000) -> None:
    pyfiles = [p for p in files if p.suffix == ".py"]
    print_header("PYTHON SOURCE SYNTAX (STATIC; FILES ARE NOT EXECUTED)")
    if not pyfiles:
        print("No Python files found in selected roots.")
        return
    errors = []
    skipped = 0
    for path in pyfiles[:limit]:
        try:
            if path.stat().st_size > 2_000_000:
                skipped += 1
                continue
            source = path.read_text(encoding="utf-8", errors="replace")
            ast.parse(source, filename=str(path))
        except (SyntaxError, ValueError) as exc:
            errors.append((path, getattr(exc, "lineno", None), str(exc)))
        except OSError as exc:
            errors.append((path, None, f"read error: {exc}"))
    print(f"Parsed: {min(len(pyfiles), limit) - skipped}; syntax/read errors: {len(errors)}; skipped large files: {skipped}")
    if len(pyfiles) > limit:
        print(f"  Scan limit: only first {limit} Python files were checked.")
    for path, line, message in errors[:50]:
        where = f":{line}" if line else ""
        print(f"  BROKEN {path}{where}: {short(message, 220)}")
    if not errors:
        print("  No Python syntax errors found in the files checked. This is not a functional test.")


def inspect_conflict_markers(files: Sequence[Path]) -> None:
    print_header("MERGE-CONFLICT MARKER CHECK")
    markers = re.compile(r"^(<<<<<<< |=======\s*$|>>>>>>> )")
    checked = 0
    hits: List[Tuple[Path, int]] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            checked += 1
            with path.open("r", errors="replace") as f:
                for n, line in enumerate(f, 1):
                    if markers.search(line):
                        hits.append((path, n))
                        if len(hits) >= 100:
                            break
        except OSError:
            continue
        if len(hits) >= 100:
            break
    print(f"Text files checked: {checked}; marker matches: {len(hits)}")
    for path, line in hits[:50]:
        print(f"  CHECK {path}:{line}")
    if not hits:
        print("  No conflict markers found in checked text files.")


def process_start_time(pid: int, stat_text: str) -> str:
    try:
        close = stat_text.rfind(")")
        fields = stat_text[close + 2 :].split()
        start_ticks = int(fields[19])
        hz = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        btime = 0
        with open("/proc/stat", "r") as f:
            for line in f:
                if line.startswith("btime "):
                    btime = int(line.split()[1])
                    break
        epoch = btime + start_ticks / hz
        return dt.datetime.fromtimestamp(epoch).astimezone().isoformat(timespec="seconds")
    except Exception:
        return "unknown"


def process_user(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("Uid:"):
                    uid = int(line.split()[1])
                    return pwd.getpwuid(uid).pw_name
    except Exception:
        pass
    return "?"


def process_cgroup(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cgroup", "r") as f:
            text = f.read()
        match = re.search(r"/(?:system\.slice|user\.slice)/[^\n]+", text)
        if match:
            return match.group(0)
        return short(text.replace("\n", " "), 120) if text.strip() else "unknown"
    except OSError:
        return "unavailable"


def root_tokens(roots: Sequence[Path]) -> List[str]:
    return [str(p).lower() for p in roots]


def is_relevant_process(cmd: str, exe: str, cwd: str, roots: Sequence[Path]) -> bool:
    blob = f"{cmd} {exe} {cwd}".lower()
    if any(token and token in blob for token in root_tokens(roots)):
        return True
    return any(marker in blob for marker in PROCESS_MARKERS)


def inspect_processes(roots: Sequence[Path]) -> List[Dict[str, Any]]:
    print_header("MATCHING LIVE PROCESSES (PROCESS EXISTENCE IS NOT HEALTH)")
    rows: List[Dict[str, Any]] = []
    try:
        pids = [int(x) for x in os.listdir("/proc") if x.isdigit()]
    except OSError as exc:
        print(f"Cannot read /proc: {exc}")
        return rows
    for pid in pids:
        if pid == os.getpid():
            continue
        try:
            raw = Path(f"/proc/{pid}/cmdline").read_bytes()
            cmd = raw.replace(b"\0", b" ").decode(errors="replace").strip()
            if not cmd:
                continue
            exe = os.readlink(f"/proc/{pid}/exe")
            cwd = os.readlink(f"/proc/{pid}/cwd")
            if not is_relevant_process(cmd, exe, cwd, roots):
                continue
            stat_text = Path(f"/proc/{pid}/stat").read_text(errors="replace")
            close = stat_text.rfind(")")
            fields = stat_text[close + 2 :].split()
            ppid = int(fields[1])
            rows.append({
                "pid": pid,
                "ppid": ppid,
                "user": process_user(pid),
                "start": process_start_time(pid, stat_text),
                "cmd": short(cmd, 220),
                "exe": short(exe, 180),
                "cwd": short(cwd, 180),
                "cgroup": process_cgroup(pid),
            })
        except (FileNotFoundError, ProcessLookupError, PermissionError, OSError, ValueError, IndexError):
            continue
    rows.sort(key=lambda item: item["pid"])
    if not rows:
        print("No matching processes found (or process details were inaccessible).")
        return rows
    for row in rows[:200]:
        print(f"  PID {row['pid']} PPID {row['ppid']} user={row['user']} started={row['start']}")
        print(f"    cmd: {row['cmd']}")
        print(f"    exe: {row['exe']}")
        print(f"    cwd: {row['cwd']}")
        print(f"    cgroup: {row['cgroup']}")
    if len(rows) > 200:
        print(f"  Output capped at 200 of {len(rows)} matching processes.")
    return rows


def inspect_sockets(processes: Sequence[Dict[str, Any]]) -> None:
    print_header("LISTENING SOCKETS (NO CONNECTIONS ARE MADE)")
    if not shutil.which("ss"):
        print("ss is not installed; listener inventory unavailable.")
        return
    pids = {str(p["pid"]) for p in processes}
    selected = []
    for args in (["ss", "-ltnp"], ["ss", "-lunp"]):
        code, out, err = run_command(args, timeout=5)
        if code != 0:
            print(f"  {' '.join(args)} unavailable: {short(err or out, 200)}")
            continue
        for line in out.splitlines()[1:]:
            port_match = re.search(r":(\d+)\s", line)
            port = port_match.group(1) if port_match else ""
            has_matching_pid = any(re.search(rf"\bpid={re.escape(pid)}\b", line) for pid in pids)
            known_port = port in {"8080", "8005", "9872", "8899", "8900"}
            text_match = any(marker in line.lower() for marker in PROCESS_MARKERS)
            if has_matching_pid or known_port or text_match:
                selected.append(line.strip())
    if not selected:
        print("No relevant listeners identified (or ss lacked permission/details).")
    for line in selected[:60]:
        print("  " + short(line, 260))
    if len(selected) > 60:
        print(f"  Output capped at 60 of {len(selected)} matching listener rows.")


def matching_units() -> List[str]:
    if not shutil.which("systemctl"):
        return []
    code, out, _ = run_command(["systemctl", "list-units", "--all", "--type=service", "--no-legend", "--no-pager"], timeout=8)
    units = set()
    if code == 0:
        for line in out.splitlines():
            fields = line.split()
            if fields and any(k in fields[0].lower() for k in ("sip", "sovereign", "toll", "ingress")):
                units.add(fields[0])
    units.add(DEFAULT_UNIT)
    return sorted(units)


def inspect_systemd() -> List[str]:
    print_header("MATCHING SYSTEMD SERVICES")
    if not shutil.which("systemctl"):
        print("systemctl unavailable; service ownership cannot be checked.")
        return []
    units = matching_units()
    properties = [
        "Id", "LoadState", "ActiveState", "SubState", "MainPID", "User",
        "ExecStart", "StandardOutput", "StandardError", "Restart", "FragmentPath", "ControlGroup",
    ]
    found: List[str] = []
    for unit in units:
        code, out, err = run_command(["systemctl", "show", unit, "--no-pager", "--property=" + ",".join(properties)], timeout=6)
        if code != 0 or not out.strip():
            continue
        mapping = {}
        for line in out.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                mapping[key] = value
        if mapping.get("LoadState") == "not-found":
            continue
        found.append(unit)
        print(f"  {unit}: {mapping.get('LoadState','?')} / {mapping.get('ActiveState','?')} / {mapping.get('SubState','?')}")
        for key in ("MainPID", "User", "Restart", "StandardOutput", "StandardError", "FragmentPath", "ControlGroup", "ExecStart"):
            value = mapping.get(key, "")
            if value:
                print(f"    {key}: {short(value, 260)}")
    if not found:
        print("No matching loaded SIP/Sovereign/Toll services found (or systemd access unavailable).")
    return found


def is_log_candidate(path: Path, root: Path) -> bool:
    name = path.name.lower()
    rel = str(path.relative_to(root)).lower()
    if name in KNOWN_LOG_NAMES:
        return True
    if any(name.endswith(suffix) for suffix in LOG_SUFFIXES):
        return True
    if ".log." in name or name.endswith((".stdout", ".stderr")):
        return True
    if name.endswith(".json") and any(token in name for token in ("audit", "telemetry", "health", "status")):
        return True
    if "log" in name and path.suffix.lower() in TEXT_SUFFIXES:
        return True
    # In log-oriented directories, include actual log formats only; do not
    # misclassify benchmark CSVs or ordinary evidence documents as runtime logs.
    return (
        any(part in rel.split("/") for part in ("logs", "evidence", "telemetry"))
        and path.suffix.lower() in {".log", ".out", ".err", ".jsonl"}
    )


def discover_logs(roots: Sequence[Path], max_files: int) -> List[Path]:
    candidates: List[Path] = []
    seen = set()
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        files, _ = walk_project(root, max_files=25000)
        for path in files:
            if not is_log_candidate(path, root):
                continue
            try:
                if not path.is_file() or path.stat().st_size > 2_000_000_000:
                    continue
            except OSError:
                continue
            resolved = str(path.resolve())
            if resolved not in seen:
                seen.add(resolved)
                candidates.append(path)
    # Prefer explicitly known/high-signal sources, then newest files.
    candidates.sort(key=lambda p: (p.name not in KNOWN_LOG_NAMES, -safe_mtime(p), str(p)))
    return candidates[:max_files]


def read_tail(path: Path, count: int, max_bytes: int = 512_000) -> List[str]:
    """Read at most max_bytes from a file's end; do not load large logs wholesale."""
    with path.open("rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        start = max(0, size - max_bytes)
        f.seek(start)
        data = f.read(max_bytes)
    lines = data.decode("utf-8", errors="replace").splitlines()
    if start > 0 and lines:
        lines = lines[1:]  # first line may be a partial fragment
    return lines[-count:]


def source_label(path: Path) -> str:
    text = str(path).lower()
    name = path.name.lower()
    if "sip_daemon" in name or "sip_daemon" in text:
        return "SIP-DAEMON"
    if "toll" in text or "ingress" in text:
        return "TOLL-BRIDGE"
    if "supervisor" in text or "sovereign_master" in name:
        return "SUPERVISOR/WORKER"
    if "telemetry" in text or "audit" in name:
        return "TELEMETRY"
    if "worker" in name:
        return "WORKER"
    return "FILE-LOG"


def parse_timestamp(line: str) -> Optional[dt.datetime]:
    match = TIMESTAMP_RE.search(line)
    if not match:
        return None
    stamp = match.group("stamp")
    if stamp.endswith("Z"):
        stamp = stamp[:-1] + "+00:00"
    # Convert compact offsets such as +0000 into +00:00.
    if re.search(r"[+-]\d{4}$", stamp):
        stamp = stamp[:-2] + ":" + stamp[-2:]
    try:
        value = dt.datetime.fromisoformat(stamp)
        if value.tzinfo is None:
            value = value.astimezone()
        return value
    except ValueError:
        return None


def inspect_file_logs(roots: Sequence[Path], last: int, max_files: int) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    print_header(f"RECENT FILE LOGS: UP TO {last} LINES PER SOURCE")
    paths = discover_logs(roots, max_files)
    entries: List[Dict[str, Any]] = []
    coverage: List[Tuple[str, str]] = []
    if not paths:
        print("No candidate log files found in selected roots.")
        return entries, coverage
    for path in paths:
        label = source_label(path)
        try:
            lines = read_tail(path, last)
            stat = path.stat()
            coverage.append((label, f"FILE entries={len(lines)}; {file_age(path)}; {bytes_human(stat.st_size)}"))
            print(f"\n--- [{label}] {path} | {bytes_human(stat.st_size)} | modified {file_age(path)}")
            if not lines:
                print("  EMPTY or unreadable tail.")
                continue
            err_count = sum(bool(ERROR_RE.search(line)) for line in lines)
            warn_count = sum(bool(WARN_RE.search(line)) for line in lines)
            print(f"  Sample markers: errors={err_count}, warnings/retries/timeouts={warn_count} (keyword scan only)")
            for line in lines:
                clean = redact(line)
                print("  " + short(clean, 500))
                stamp = parse_timestamp(line)
                entries.append({
                    "sort_time": stamp.timestamp() if stamp else stat.st_mtime,
                    "time_text": stamp.isoformat(timespec="seconds") if stamp else f"file-time~{file_age(path)}",
                    "source": label,
                    "message": short(clean, 500),
                    "path": str(path),
                })
        except PermissionError:
            coverage.append((label, "FILE INACCESSIBLE: permission denied"))
            print(f"\n--- [{label}] {path} | INACCESSIBLE: permission denied")
        except OSError as exc:
            coverage.append((label, f"FILE ERROR: {exc}"))
            print(f"\n--- [{label}] {path} | READ ERROR: {exc}")
    if len(discover_logs(roots, max_files + 1)) > max_files:
        print(f"\n  File-source display capped at {max_files}; raise --max-log-files to inspect more.")
    return entries, coverage


def read_journal(unit: str, last: int) -> Tuple[List[Dict[str, Any]], str]:
    if not shutil.which("journalctl"):
        return [], "journalctl unavailable"
    code, out, err = run_command(
        ["journalctl", "-u", unit, "-n", str(last), "--no-pager", "-o", "json"], timeout=8
    )
    if code != 0:
        return [], short(err.strip() or out.strip() or f"journalctl exit {code}", 260)
    items: List[Dict[str, Any]] = []
    for raw in out.splitlines():
        try:
            obj = json.loads(raw)
            message = str(obj.get("MESSAGE", ""))
            if not message:
                continue
            usec = int(obj.get("__REALTIME_TIMESTAMP", "0"))
            when = usec / 1_000_000 if usec else time.time()
            stamp = dt.datetime.fromtimestamp(when).astimezone().isoformat(timespec="seconds")
            pid = str(obj.get("_PID", "?"))
            items.append({
                "sort_time": when,
                "time_text": stamp,
                "source": f"JOURNAL:{unit}",
                "message": short(message, 500),
                "path": f"unit={unit}; pid={pid}",
            })
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
    return items, "OK" if items else "EMPTY: no entries returned"


def inspect_journals(units: Sequence[str], last: int) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    print_header(f"SYSTEMD JOURNAL: UP TO {last} ENTRIES PER UNIT")
    entries: List[Dict[str, Any]] = []
    coverage: List[Tuple[str, str]] = []
    if not units:
        print("No matching units discovered. The known supervisor unit will still be queried.")
        units = [DEFAULT_UNIT]
    for unit in units:
        rows, status = read_journal(unit, last)
        coverage.append((f"JOURNAL:{unit}", f"{status}; entries={len(rows)}"))
        print(f"\n--- JOURNAL {unit}: {status}")
        for row in rows:
            print(f"  {row['time_text']} [{row['source']}] {row['message']}")
        entries.extend(rows)
    return entries, coverage


def inspect_tests(files: Sequence[Path], limit: int = 25) -> None:
    print_header("TEST/LAUNCH SCRIPT REFERENCES (STATIC SEARCH; NOT EXECUTED)")
    candidates = [p for p in files if p.name.lower() in {
        "run_test.py", "test_toll_bridge.py", "test_ingress.py", "sip_client.py",
        "sip_master_supervisor.py", "sip_watcher.py", "permanent_singelton_guard.py",
        "permanent_singleton_guard.py",
    }]
    if not candidates:
        print("No specifically named test/launch scripts found in selected roots.")
        return
    pattern = re.compile(r"(https?://|localhost|127\.0\.0\.1|0\.0\.0\.0|:8080|:8005|:9872|requests\.|urlopen|subprocess|Popen|Popen|Popen|kill\(|system\(|exec\(|sqlite3|INSERT|UPDATE|DELETE|POST )", re.I)
    for path in candidates[:limit]:
        print(f"\n--- {path}")
        try:
            with path.open("r", errors="replace") as f:
                hits = [(n, line.strip()) for n, line in enumerate(f, 1) if pattern.search(line)]
            if not hits:
                print("  No network/process/database markers found by the simple scan.")
            for n, line in hits[:20]:
                print(f"  L{n}: {short(line, 240)}")
            if len(hits) > 20:
                print(f"  {len(hits) - 20} additional matching lines omitted.")
        except OSError as exc:
            print(f"  Cannot read: {exc}")


def summarize_components(processes: Sequence[Dict[str, Any]], units: Sequence[str], coverage: Sequence[Tuple[str, str]], roots: Sequence[Path]) -> None:
    print_header("COMPONENT EVIDENCE SUMMARY (NOT A FUNCTIONAL HEALTH CERTIFICATION)")
    process_text = " ".join(p["cmd"].lower() for p in processes)

    def log_state(*needles: str) -> str:
        matches = [(name.lower().replace("-", "_"), detail.lower()) for name, detail in coverage
                   if any(needle in name.lower().replace("-", "_") for needle in needles)]
        if not matches:
            return "NO SOURCE FOUND"
        details = " ".join(detail for _, detail in matches)
        if "permission denied" in details or "inaccessible" in details:
            return "SOURCE INACCESSIBLE"
        if "entries=0" in details or "empty:" in details:
            return "SOURCE EMPTY (NO RECENT ENTRIES)"
        if re.search(r"entries=[1-9]\d*", details):
            return "RECENT ENTRIES READ"
        return "SOURCE STATUS UNKNOWN"

    checks = [
        ("SIP daemon", "sip_daemon" in process_text, log_state("sip_daemon")),
        ("Master supervisor", "sip_master_supervisor" in process_text,
         log_state("supervisor")),
        ("Toll Bridge / ingress", "ingress" in process_text or "toll_bridge" in process_text,
         log_state("toll", "ingress")),
        ("Other matching workers", any(any(x in p["cmd"].lower() for x in ("worker", "watcher", "validator", "guard")) for p in processes),
         log_state("worker")),
    ]
    for name, active, log_status in checks:
        runtime = "PROCESS SEEN" if active else "NOT SEEN / UNKNOWN"
        print(f"  {name}: {runtime}; log status={log_status}; functional status=UNVERIFIED")
    print("  No end-to-end event was sent. Port listeners/processes/log snippets do not prove correct data flow.")
    print("  Log keyword counts are heuristic and cannot determine the quality/correctness of work.")
    print("  Roots inspected: " + (", ".join(str(p) for p in roots) if roots else "none; pass --root PATH"))


def combined_batch(entries: Sequence[Dict[str, Any]], last: int) -> None:
    print_header(f"COMBINED MOST RECENT {last} ENTRIES (FROM SOURCES READABLE ABOVE)")
    if not entries:
        print("No log entries were readable. This does not mean the system is healthy.")
        return
    rows = sorted(entries, key=lambda e: e["sort_time"])[-last:]
    for row in rows:
        print(f"  {row['time_text']} [{row['source']}] {row['message']}")
    print("  Combined view covers only the sources read by this run; missing sources are excluded.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only SIP workspace/runtime/log review; no services are modified."
    )
    parser.add_argument("--root", action="append", type=Path, default=None,
                        help="Project root to inspect; repeat for additional workspaces. Defaults to existing known roots under the invoking user's home.")
    parser.add_argument("--last", type=int, default=10,
                        help="Entries/lines per source and combined batch (default: 10). Range: 1-1000.")
    parser.add_argument("--max-log-files", type=int, default=30,
                        help="Maximum candidate log files to read (default: 30; range: 1-200).")
    parser.add_argument("--skip-journal", action="store_true",
                        help="Skip journal queries.")
    parser.add_argument("--skip-source-checks", action="store_true",
                        help="Skip Python syntax, conflict-marker, manifest, and script-reference checks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.last < 1 or args.last > 1000:
        print("ERROR: --last must be between 1 and 1000", file=sys.stderr)
        return 2
    if args.max_log_files < 1 or args.max_log_files > 200:
        print("ERROR: --max-log-files must be between 1 and 200", file=sys.stderr)
        return 2
    roots = [p.expanduser().resolve() for p in args.root] if args.root else default_roots()
    print(f"SIP SYSTEM REVIEW v{VERSION} | {dt.datetime.now().astimezone().isoformat(timespec='seconds')}")
    print("MODE: READ-ONLY | No network probes, service actions, file writes, or permission changes.")
    print("NOTE: This reviews observable evidence; it cannot certify end-to-end correctness or judge all source-code quality.")
    if not roots:
        print("No default workspace roots found. Re-run with --root /absolute/path/to/workspace.")
    files = inventory_roots(roots, args.last)
    if not args.skip_source_checks:
        inspect_manifests(files, args.last)
        inspect_python_syntax(files)
        inspect_conflict_markers(files)
        inspect_tests(files)
    processes = inspect_processes(roots)
    inspect_sockets(processes)
    units = inspect_systemd()
    file_entries, file_coverage = inspect_file_logs(roots, args.last, args.max_log_files)
    journal_entries: List[Dict[str, Any]] = []
    journal_coverage: List[Tuple[str, str]] = []
    if not args.skip_journal:
        journal_entries, journal_coverage = inspect_journals(units, args.last)
    coverage = file_coverage + journal_coverage
    summarize_components(processes, units, coverage, roots)
    combined_batch(file_entries + journal_entries, args.last)
    print_header("SAFE NEXT-STEP GUIDANCE")
    print("  Use the evidence above to identify gaps. Do not infer that a component is healthy merely because it is running.")
    print("  Review any suggested test/launch script before executing it; this program did not execute project code.")
    print("  Log text may contain private payloads even after common credentials are redacted; review before sharing output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
