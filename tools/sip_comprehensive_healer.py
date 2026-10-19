#!/usr/bin/env python3
"""
SIP Comprehensive Service Reconciler

Purpose:
    Audit and cautiously repair the SIP / Toll Bridge service ecosystem.

Design rules:
    - Port 8080 is the primary Toll Bridge traffic authority.
    - Unknown processes are never killed automatically.
    - Commands are executed as argument lists; shell=True is never used.
    - Every service is processed independently.
    - Each service has a bounded timeout.
    - Failures are recorded and processing continues.
    - State is checkpointed so an interrupted run can resume.
    - No fake modules, heartbeat files, credentials, or configuration are created.
    - This tool does not change ports automatically. Port reassignment requires
      an explicit configuration change by the operator.

Usage:
    sudo python3 tools/sip_comprehensive_healer.py

Optional:
    sudo python3 tools/sip_comprehensive_healer.py --audit-only
    sudo python3 tools/sip_comprehensive_healer.py --resume
    sudo python3 tools/sip_comprehensive_healer.py --retry-failed
    sudo python3 tools/sip_comprehensive_healer.py --service tollbridge.service
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PRIMARY_BRIDGE_PORT = 8080
SERVICE_TIMEOUT_SECONDS = 30
COMMAND_TIMEOUT_SECONDS = 15
JOURNAL_LINES = 120
RESTART_ATTEMPTS = 2
RESTART_BACKOFF_SECONDS = 3

DEFAULT_STATE_ROOT = pathlib.Path(
    os.environ.get(
        "SIP_HEALER_STATE_DIR",
        "/var/tmp/sip-comprehensive-healer",
    )
)

LOG_ROOT = DEFAULT_STATE_ROOT / "logs"
REPORT_ROOT = DEFAULT_STATE_ROOT / "reports"
CHECKPOINT_PATH = DEFAULT_STATE_ROOT / "checkpoint.json"
FINAL_REPORT_PATH = REPORT_ROOT / "final_report.json"
UNRESOLVED_PATH = REPORT_ROOT / "unresolved_services.json"

# These patterns identify the SIP ecosystem. Other operating-system services
# are inventoried but not restarted by default.
ECOSYSTEM_PATTERNS = (
    "sip",
    "sovereign",
    "toll",
    "bridge",
    "mesh",
    "commons",
    "geyser",
    "xdp",
    "ebpf",
    "producer",
    "consumer",
    "engine",
    "validator",
    "cloudflared",
    "redis",
    "solana",
    "apex",
)

# These patterns identify likely primary-bridge units.
PRIMARY_BRIDGE_PATTERNS = (
    "tollbridge",
    "toll-bridge",
    "toll_bridge",
    "bridge",
    "sip-ingress",
    "sip_ingress",
    "sip-gateway",
    "sip_gateway",
)

# Never restart these automatically. They may be essential to the host.
NEVER_AUTO_RESTART = (
    "ssh",
    "sshd",
    "systemd",
    "dbus",
    "network",
    "networking",
    "ufw",
    "firewalld",
    "docker",
    "containerd",
)

# Error signatures that matter for this project.
ERROR_PATTERNS = (
    re.compile(r"address already in use", re.I),
    re.compile(r"errno\s*98", re.I),
    re.compile(r"error\s*98", re.I),
    re.compile(r"bind\(\).*failed", re.I),
    re.compile(r"failed to bind", re.I),
    re.compile(r"cannot assign requested address", re.I),
    re.compile(r"connection refused", re.I),
    re.compile(r"permission denied", re.I),
    re.compile(r"no such file or directory", re.I),
    re.compile(r"module not found", re.I),
    re.compile(r"importerror", re.I),
    re.compile(r"segmentation fault", re.I),
    re.compile(r"out of memory", re.I),
)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CommandResult:
    argv: List[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration_seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


@dataclass
class PortOwner:
    address: str
    port: int
    process_description: str
    pid: Optional[int] = None
    unit: Optional[str] = None


@dataclass
class ServiceRecord:
    name: str
    load_state: str = ""
    active_state: str = ""
    sub_state: str = ""
    unit_file_state: str = ""
    result: str = ""
    exec_main_pid: str = ""
    exec_start: str = ""
    fragment_path: str = ""
    restart_count: str = ""
    memory_current: str = ""
    cpu_usage_nsec: str = ""
    dependencies: List[str] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)
    port_owners: List[Dict[str, Any]] = field(default_factory=list)
    journal: str = ""
    detected_errors: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    unresolved_reasons: List[str] = field(default_factory=list)
    final_state: str = ""
    repaired: bool = False
    skipped: bool = False
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# General utilities
# ---------------------------------------------------------------------------

RUNNING = True


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe_mkdir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: pathlib.Path, text: str) -> None:
    safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def write_json(path: pathlib.Path, value: Any) -> None:
    safe_mkdir(path.parent)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def normalize_service_name(name: str) -> str:
    return name.strip()


def is_ecosystem_service(name: str) -> bool:
    lowered = name.lower()
    return any(pattern in lowered for pattern in ECOSYSTEM_PATTERNS)


def is_never_auto_restart(name: str) -> bool:
    lowered = name.lower()
    return any(pattern in lowered for pattern in NEVER_AUTO_RESTART)


def looks_like_primary_bridge(name: str) -> bool:
    lowered = name.lower()
    return any(pattern in lowered for pattern in PRIMARY_BRIDGE_PATTERNS)


def command_display(argv: Sequence[str]) -> str:
    return shlex.join(list(argv))


def run_command(
    argv: Sequence[str],
    timeout: int = COMMAND_TIMEOUT_SECONDS,
    check: bool = False,
) -> CommandResult:
    started = time.monotonic()
    argv_list = [str(x) for x in argv]

    try:
        completed = subprocess.run(
            argv_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        result = CommandResult(
            argv=argv_list,
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            duration_seconds=time.monotonic() - started,
        )
    except subprocess.TimeoutExpired as exc:
        result = CommandResult(
            argv=argv_list,
            returncode=124,
            stdout=(exc.stdout or "").strip()
            if isinstance(exc.stdout, str)
            else "",
            stderr=(exc.stderr or "").strip()
            if isinstance(exc.stderr, str)
            else "",
            timed_out=True,
            duration_seconds=time.monotonic() - started,
        )
    except FileNotFoundError as exc:
        result = CommandResult(
            argv=argv_list,
            returncode=127,
            stderr=str(exc),
            duration_seconds=time.monotonic() - started,
        )
    except Exception as exc:
        result = CommandResult(
            argv=argv_list,
            returncode=1,
            stderr=f"{type(exc).__name__}: {exc}",
            duration_seconds=time.monotonic() - started,
        )

    if check and not result.ok:
        raise RuntimeError(
            f"Command failed: {command_display(argv_list)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    return result


def privileged_command(
    argv: Sequence[str],
    timeout: int = COMMAND_TIMEOUT_SECONDS,
) -> CommandResult:
    """
    Run a command with sudo only when the current process is not root.

    The command remains an argument list. No shell interpolation occurs.
    """
    if os.geteuid() == 0:
        return run_command(argv, timeout=timeout)

    return run_command(["sudo", *argv], timeout=timeout)


def save_checkpoint(
    completed: Iterable[str],
    records: Dict[str, ServiceRecord],
    metadata: Dict[str, Any],
) -> None:
    payload = {
        "updated_at": now_utc(),
        "completed_services": sorted(set(completed)),
        "records": {k: asdict(v) for k, v in records.items()},
        "metadata": metadata,
    }
    write_json(CHECKPOINT_PATH, payload)


def load_checkpoint() -> Tuple[set[str], Dict[str, ServiceRecord], Dict[str, Any]]:
    if not CHECKPOINT_PATH.exists():
        return set(), {}, {}

    try:
        payload = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return set(), {}, {}

    completed = set(payload.get("completed_services", []))
    records: Dict[str, ServiceRecord] = {}

    for name, raw in payload.get("records", {}).items():
        try:
            records[name] = ServiceRecord(**raw)
        except TypeError:
            continue

    metadata = payload.get("metadata", {})
    return completed, records, metadata


# ---------------------------------------------------------------------------
# Service discovery
# ---------------------------------------------------------------------------

def discover_services() -> List[str]:
    """
    Discover all loaded system services.

    The returned list is complete. Later policy determines which services may
    be restarted. This prevents a name filter from hiding services.
    """
    result = run_command(
        [
            "systemctl",
            "list-unit-files",
            "--type=service",
            "--all",
            "--no-legend",
            "--no-pager",
        ],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    if not result.ok:
        raise RuntimeError(
            "Unable to enumerate systemd services:\n"
            + (result.stderr or result.stdout)
        )

    services: set[str] = set()

    for line in result.stdout.splitlines():
        parts = line.split()
        if not parts:
            continue

        name = normalize_service_name(parts[0])

        if name.endswith(".service"):
            services.add(name)

    return sorted(services)


def service_show(name: str) -> Dict[str, str]:
    fields = [
        "Id",
        "LoadState",
        "ActiveState",
        "SubState",
        "UnitFileState",
        "Result",
        "ExecMainPID",
        "ExecStart",
        "FragmentPath",
        "NRestarts",
        "MemoryCurrent",
        "CPUUsageNSec",
        "Requires",
        "After",
        "Wants",
    ]

    result = run_command(
        ["systemctl", "show", name, "--no-pager", *[
            f"--property={field}" for field in fields
        ]],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    values: Dict[str, str] = {}

    if not result.ok:
        return values

    for line in result.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value

    return values


def dependency_names(values: Dict[str, str]) -> List[str]:
    raw = " ".join(
        values.get(key, "")
        for key in ("Requires", "After", "Wants")
    )

    return sorted(
        {
            item.strip()
            for item in raw.split()
            if item.strip().endswith(".service")
        }
    )


# ---------------------------------------------------------------------------
# Port and process inspection
# ---------------------------------------------------------------------------

def parse_port_from_address(value: str) -> Optional[int]:
    value = value.strip()

    if not value:
        return None

    if value.startswith("["):
        match = re.search(r"\]:(\d+)$", value)
    else:
        match = re.search(r":(\d+)$", value)

    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


def inspect_listening_ports() -> List[PortOwner]:
    """
    Read TCP listeners through ss.

    This is intentionally read-only. It does not kill processes and does not
    infer that every listener is wrong.
    """
    result = run_command(
        ["ss", "-H", "-ltnp"],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    if not result.ok:
        return []

    owners: List[PortOwner] = []

    for line in result.stdout.splitlines():
        fields = line.split(None, 5)

        if len(fields) < 4:
            continue

        local_address = fields[3]
        process_description = fields[5] if len(fields) >= 6 else ""

        port = parse_port_from_address(local_address)
        if port is None:
            continue

        pid: Optional[int] = None
        pid_match = re.search(r"pid=(\d+)", process_description)

        if pid_match:
            try:
                pid = int(pid_match.group(1))
            except ValueError:
                pid = None

        owners.append(
            PortOwner(
                address=local_address,
                port=port,
                process_description=process_description,
                pid=pid,
            )
        )

    return owners


def process_command(pid: int) -> str:
    if pid <= 0:
        return ""

    result = run_command(
        ["ps", "-p", str(pid), "-o", "args="],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    return result.stdout.strip()


def process_systemd_unit(pid: int) -> Optional[str]:
    if pid <= 0:
        return None

    result = run_command(
        ["systemctl", "status", str(pid), "--no-pager", "--plain"],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    match = re.search(r"Loaded:\s+loaded\s+\(([^;]+)", result.stdout)
    if match:
        unit = pathlib.Path(match.group(1)).name
        if unit.endswith(".service"):
            return unit

    return None


def ports_for_service(
    service_name: str,
    owners: List[PortOwner],
) -> Tuple[List[int], List[Dict[str, Any]]]:
    values: List[int] = []
    serialized: List[Dict[str, Any]] = []

    for owner in owners:
        unit = owner.unit

        if unit is None and owner.pid:
            unit = process_systemd_unit(owner.pid)

        owner.unit = unit

        process_text = owner.process_description
        if owner.pid:
            process_text += " " + process_command(owner.pid)

        belongs = (
            unit == service_name
            or service_name.lower() in process_text.lower()
            or service_name.removesuffix(".service").lower()
            in process_text.lower()
        )

        if belongs:
            values.append(owner.port)
            serialized.append(asdict(owner))

    return sorted(set(values)), serialized


def primary_port_owners(owners: List[PortOwner]) -> List[PortOwner]:
    return [owner for owner in owners if owner.port == PRIMARY_BRIDGE_PORT]


# ---------------------------------------------------------------------------
# Journald diagnostics
# ---------------------------------------------------------------------------

def read_journal(service_name: str) -> str:
    result = run_command(
        [
            "journalctl",
            "-u",
            service_name,
            "-n",
            str(JOURNAL_LINES),
            "--no-pager",
            "--output=short-iso",
        ],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    if result.ok:
        return result.stdout

    # Retry with sudo if ordinary journal access is restricted.
    privileged = privileged_command(
        [
            "journalctl",
            "-u",
            service_name,
            "-n",
            str(JOURNAL_LINES),
            "--no-pager",
            "--output=short-iso",
        ],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    return privileged.stdout if privileged.ok else (
        result.stderr or privileged.stderr
    )


def detect_errors(text: str) -> List[str]:
    found: List[str] = []

    for line in text.splitlines():
        for pattern in ERROR_PATTERNS:
            if pattern.search(line):
                clean = line.strip()
                if clean and clean not in found:
                    found.append(clean)
                break

    return found[-30:]


def save_service_log(record: ServiceRecord) -> pathlib.Path:
    path = LOG_ROOT / (
        record.name.replace("/", "_").replace(":", "_") + ".log"
    )

    content = [
        f"service={record.name}",
        f"captured_at={now_utc()}",
        f"active_state={record.active_state}",
        f"sub_state={record.sub_state}",
        f"result={record.result}",
        "",
        "=== EXEC START ===",
        record.exec_start,
        "",
        "=== DETECTED PORTS ===",
        json.dumps(record.port_owners, indent=2),
        "",
        "=== DETECTED ERRORS ===",
        *record.detected_errors,
        "",
        "=== JOURNAL ===",
        record.journal,
        "",
    ]

    write_text(path, "\n".join(content))
    return path


# ---------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------

def diagnose_port_conflicts(
    record: ServiceRecord,
    all_owners: List[PortOwner],
) -> None:
    if PRIMARY_BRIDGE_PORT not in record.ports:
        return

    owners = primary_port_owners(all_owners)

    if len(owners) <= 1:
        return

    record.unresolved_reasons.append(
        f"Multiple listeners detected on primary port "
        f"{PRIMARY_BRIDGE_PORT}"
    )

    for owner in owners:
        record.unresolved_reasons.append(
            "port-8080-owner: "
            + json.dumps(asdict(owner), sort_keys=True)
        )


def diagnose_primary_bridge(
    record: ServiceRecord,
    all_owners: List[PortOwner],
) -> None:
    if not looks_like_primary_bridge(record.name):
        return

    owners = primary_port_owners(all_owners)

    if record.active_state == "active" and owners:
        record.actions.append(
            f"primary bridge listener observed on port {PRIMARY_BRIDGE_PORT}"
        )
        return

    if record.active_state != "active" and owners:
        record.unresolved_reasons.append(
            f"port {PRIMARY_BRIDGE_PORT} is occupied while "
            f"{record.name} is not active"
        )

    if record.active_state == "active" and not owners:
        record.unresolved_reasons.append(
            f"{record.name} reports active but no listener was observed "
            f"on primary port {PRIMARY_BRIDGE_PORT}"
        )


def build_record(
    service_name: str,
    all_owners: List[PortOwner],
) -> ServiceRecord:
    started = time.monotonic()
    values = service_show(service_name)

    record = ServiceRecord(
        name=service_name,
        load_state=values.get("LoadState", ""),
        active_state=values.get("ActiveState", ""),
        sub_state=values.get("SubState", ""),
        unit_file_state=values.get("UnitFileState", ""),
        result=values.get("Result", ""),
        exec_main_pid=values.get("ExecMainPID", ""),
        exec_start=values.get("ExecStart", ""),
        fragment_path=values.get("FragmentPath", ""),
        restart_count=values.get("NRestarts", ""),
        memory_current=values.get("MemoryCurrent", ""),
        cpu_usage_nsec=values.get("CPUUsageNSec", ""),
        dependencies=dependency_names(values),
    )

    record.ports, record.port_owners = ports_for_service(
        service_name,
        all_owners,
    )

    record.journal = read_journal(service_name)
    record.detected_errors = detect_errors(record.journal)

    diagnose_port_conflicts(record, all_owners)
    diagnose_primary_bridge(record, all_owners)

    record.duration_seconds = time.monotonic() - started
    return record


# ---------------------------------------------------------------------------
# Repair policy
# ---------------------------------------------------------------------------

def should_repair(record: ServiceRecord, audit_only: bool) -> bool:
    if audit_only:
        record.skipped = True
        record.actions.append("audit-only mode; no mutation performed")
        return False

    if is_never_auto_restart(record.name):
        record.skipped = True
        record.actions.append("protected host service; automatic restart skipped")
        return False

    if not is_ecosystem_service(record.name):
        record.skipped = True
        record.actions.append("non-SIP service; inventoried but not changed")
        return False

    if record.unit_file_state == "masked":
        record.skipped = True
        record.actions.append("unit file state is masked; skipping")
        return False

    if record.unit_file_state == "disabled" and is_ecosystem_service(record.name):
        record.actions.append("service is disabled; attempting automatic enable")
        privileged_command(["systemctl", "enable", record.name])

    if record.active_state == "active" and not record.detected_errors:
        record.actions.append("already active with no detected journal errors")
        return False

    return True


def reset_failed_state(record: ServiceRecord) -> None:
    result = privileged_command(
        ["systemctl", "reset-failed", record.name],
        timeout=COMMAND_TIMEOUT_SECONDS,
    )

    if result.ok:
        record.actions.append("reset-failed completed")
    else:
        record.actions.append(
            "reset-failed failed: " + (result.stderr or result.stdout)
        )


def restart_service(record: ServiceRecord) -> bool:
    for attempt in range(1, RESTART_ATTEMPTS + 1):
        record.actions.append(f"restart attempt {attempt}")

        result = privileged_command(
            ["systemctl", "restart", record.name],
            timeout=SERVICE_TIMEOUT_SECONDS,
        )

        if result.ok:
            time.sleep(1)

            state = run_command(
                ["systemctl", "is-active", record.name],
                timeout=COMMAND_TIMEOUT_SECONDS,
            )

            if state.stdout.strip() == "active":
                record.actions.append(
                    f"restart attempt {attempt} reached active state"
                )
                record.repaired = True
                return True

            record.actions.append(
                "restart returned success but service is not active: "
                + state.stdout
            )
        else:
            details = result.stderr or result.stdout
            record.actions.append(
                f"restart attempt {attempt} failed: {details}"
            )

        if attempt < RESTART_ATTEMPTS:
            time.sleep(RESTART_BACKOFF_SECONDS)

    return False


def cautiously_repair(
    record: ServiceRecord,
    all_owners: List[PortOwner],
    audit_only: bool,
) -> None:
    if not should_repair(record, audit_only):
        return

    # Error 98 is diagnosed, not solved by killing arbitrary processes.
    if any(
        "98" in error
        or "already in use" in error.lower()
        or "failed to bind" in error.lower()
        for error in record.detected_errors
    ):
        record.actions.append(
            "bind conflict detected; unknown processes will not be killed"
        )

        occupied = [
            owner for owner in all_owners
            if owner.port == PRIMARY_BRIDGE_PORT
        ]

        if occupied and looks_like_primary_bridge(record.name):
            record.unresolved_reasons.append(
                "primary bridge bind conflict requires operator review"
            )
            record.actions.append(
                "port 8080 preserved; no automatic reassignment or kill"
            )
            return

    if record.unit_file_state == "disabled":
        res = privileged_command(["systemctl", "enable", record.name])
        if res.ok:
            record.actions.append("auto-enabled disabled service")

    if record.result == "failed" or record.active_state != "active" or record.active_state == "inactive":
        reset_failed_state(record)

    repaired = restart_service(record)

    if not repaired:
        record.unresolved_reasons.append(
            "service did not reach active state after bounded restart attempts"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def refresh_record(record: ServiceRecord) -> None:
    values = service_show(record.name)

    record.active_state = values.get("ActiveState", record.active_state)
    record.sub_state = values.get("SubState", record.sub_state)
    record.result = values.get("Result", record.result)
    record.restart_count = values.get("NRestarts", record.restart_count)
    record.exec_main_pid = values.get("ExecMainPID", record.exec_main_pid)

    fresh_journal = read_journal(record.name)
    if fresh_journal:
        record.journal = fresh_journal
        record.detected_errors = detect_errors(fresh_journal)

    if record.active_state == "active" and not record.unresolved_reasons:
        record.final_state = "healthy"
    elif record.active_state == "active":
        record.final_state = "active_with_warnings"
    else:
        record.final_state = "unresolved"


def validate_primary_port(all_owners: List[PortOwner]) -> Dict[str, Any]:
    owners = primary_port_owners(all_owners)

    return {
        "port": PRIMARY_BRIDGE_PORT,
        "listener_count": len(owners),
        "owners": [asdict(owner) for owner in owners],
        "status": (
            "one_listener"
            if len(owners) == 1
            else "no_listener"
            if len(owners) == 0
            else "multiple_listeners"
        ),
    }


def summarize(
    records: Dict[str, ServiceRecord],
    primary_port: Dict[str, Any],
) -> Dict[str, Any]:
    values = list(records.values())

    return {
        "generated_at": now_utc(),
        "service_count": len(values),
        "active": sum(x.active_state == "active" for x in values),
        "healthy": sum(x.final_state == "healthy" for x in values),
        "active_with_warnings": sum(
            x.final_state == "active_with_warnings" for x in values
        ),
        "unresolved": sum(x.final_state == "unresolved" for x in values),
        "repaired": sum(x.repaired for x in values),
        "skipped": sum(x.skipped for x in values),
        "primary_bridge": primary_port,
        "unresolved_services": [
            x.name for x in values if x.final_state == "unresolved"
        ],
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bounded SIP service discovery, diagnosis, and repair."
    )

    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Inspect and report without restarting anything.",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from the existing checkpoint.",
    )

    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Reprocess services previously marked unresolved.",
    )

    parser.add_argument(
        "--service",
        action="append",
        help="Process only this service; may be supplied multiple times.",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Discard the previous checkpoint before beginning.",
    )

    return parser.parse_args()


def install_signal_handlers() -> None:
    def stop_handler(signum: int, _frame: Any) -> None:
        global RUNNING
        RUNNING = False
        print(
            f"\nReceived signal {signum}; finishing the current service "
            "and writing the checkpoint.",
            flush=True,
        )

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)


def get_connected_ecosystem_services() -> set[str]:
    """Discover services actively connected to the primary bridge, ignoring old junk."""
    connected: set[str] = set()
    discovered = discover_services()
    primary_candidates = [
        name for name in discovered 
        if looks_like_primary_bridge(name) and service_show(name).get("LoadState") == "loaded"
    ]
    for primary in primary_candidates:
        connected.add(primary)
        result = run_command(
            ["systemctl", "list-dependencies", primary, "--plain", "--no-pager"],
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        if result.ok:
            for line in result.stdout.splitlines():
                clean_line = line.strip().removeprefix("* ").strip()
                if clean_line.endswith(".service"):
                    connected.add(clean_line)
        values = service_show(primary)
        for dep in dependency_names(values):
            connected.add(dep)
    return connected

def select_services(args: argparse.Namespace) -> List[str]:
    discovered = discover_services()

    if args.service:
        requested = set(args.service)
        return [
            name for name in discovered
            if name in requested or name.removesuffix(".service") in requested
        ]

    connected = get_connected_ecosystem_services()
    if connected:
        return sorted([name for name in discovered if name in connected])

    # Fallback to ecosystem patterns if no active cluster dependencies detected
    return [name for name in discovered if is_ecosystem_service(name)]

def main() -> int:
    global LOG_ROOT, REPORT_ROOT, CHECKPOINT_PATH
    global FINAL_REPORT_PATH, UNRESOLVED_PATH

    args = parse_args()
    install_signal_handlers()

    if args.reset and CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()

    for path in (LOG_ROOT, REPORT_ROOT):
        safe_mkdir(path)

    print("=== SIP COMPREHENSIVE SERVICE RECONCILER ===")
    print(f"Started: {now_utc()}")
    print(f"Primary Toll Bridge port: {PRIMARY_BRIDGE_PORT}")
    print(f"State directory: {DEFAULT_STATE_ROOT}")
    print(f"Audit only: {args.audit_only}")

    completed: set[str] = set()
    records: Dict[str, ServiceRecord] = {}
    metadata: Dict[str, Any] = {}

    if args.resume or args.retry_failed:
        completed, records, metadata = load_checkpoint()
        print(f"Loaded checkpoint with {len(completed)} completed services.")

    try:
        services = select_services(args)
    except Exception as exc:
        print(f"FATAL: service discovery failed: {exc}", file=sys.stderr)
        return 2

    if args.retry_failed:
        unresolved = {
            name for name, record in records.items()
            if record.final_state == "unresolved"
        }
        services = [name for name in services if name in unresolved]
        completed -= unresolved

    print(f"Discovered {len(services)} systemd service units.")

    # Inspect all listeners once per pass. This avoids inconsistent port views
    # during a single service iteration.
    all_owners = inspect_listening_ports()

    bridge_owners = primary_port_owners(all_owners)
    print(
        f"Port {PRIMARY_BRIDGE_PORT} listener count: "
        f"{len(bridge_owners)}"
    )

    for index, service_name in enumerate(services, start=1):
        if not RUNNING:
            break

        if args.resume and service_name in completed:
            print(f"[{index}/{len(services)}] SKIP checkpoint: {service_name}")
            continue

        started = time.monotonic()
        print(f"\n[{index}/{len(services)}] Processing {service_name}")

        try:
            record = build_record(service_name, all_owners)

            ecosystem = is_ecosystem_service(service_name)
            print(
                f"  active={record.active_state} "
                f"sub={record.sub_state} "
                f"result={record.result} "
                f"ecosystem={ecosystem}"
            )

            if record.detected_errors:
                print(
                    f"  detected_errors={len(record.detected_errors)}"
                )

            cautiously_repair(record, all_owners, args.audit_only)
            refresh_record(record)

            record.duration_seconds = time.monotonic() - started
            log_path = save_service_log(record)
            record.actions.append(f"log written: {log_path}")

            records[service_name] = record
            completed.add(service_name)

            print(
                f"  final={record.final_state} "
                f"repaired={record.repaired} "
                f"duration={record.duration_seconds:.1f}s"
            )

        except Exception as exc:
            failed_record = ServiceRecord(
                name=service_name,
                final_state="unresolved",
                unresolved_reasons=[
                    f"unhandled reconciler exception: "
                    f"{type(exc).__name__}: {exc}"
                ],
                duration_seconds=time.monotonic() - started,
            )

            records[service_name] = failed_record
            completed.add(service_name)

            print(
                f"  UNRESOLVED: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )

        save_checkpoint(completed, records, metadata)

    # Final fresh listener view after repairs.
    final_owners = inspect_listening_ports()
    primary_port = validate_primary_port(final_owners)

    summary = summarize(records, primary_port)
    report = {
        "tool": "sip_comprehensive_service_reconciler",
        "generated_at": now_utc(),
        "configuration": {
            "primary_bridge_port": PRIMARY_BRIDGE_PORT,
            "service_timeout_seconds": SERVICE_TIMEOUT_SECONDS,
            "command_timeout_seconds": COMMAND_TIMEOUT_SECONDS,
            "restart_attempts": RESTART_ATTEMPTS,
            "automatic_unknown_process_kill": False,
            "automatic_port_reassignment": False,
        },
        "summary": summary,
        "services": {
            name: asdict(record)
            for name, record in sorted(records.items())
        },
    }

    write_json(FINAL_REPORT_PATH, report)

    unresolved_records = {
        name: asdict(record)
        for name, record in sorted(records.items())
        if record.final_state == "unresolved"
        or record.unresolved_reasons
    }

    write_json(
        UNRESOLVED_PATH,
        {
            "generated_at": now_utc(),
            "count": len(unresolved_records),
            "services": unresolved_records,
        },
    )

    print("\n=== FINAL RECONCILIATION ===")
    print(json.dumps(summary, indent=2))
    print(f"Full report: {FINAL_REPORT_PATH}")
    print(f"Unresolved report: {UNRESOLVED_PATH}")
    print(f"Checkpoint: {CHECKPOINT_PATH}")
    print(f"Logs: {LOG_ROOT}")

    if not RUNNING:
        print(
            "Run interrupted safely. Re-run with --resume to continue."
        )
        return 3

    if summary["unresolved"] > 0:
        print(
            "Completed with unresolved services. "
            "No unresolved service was silently discarded."
        )
        return 1

    print("Completed with no unresolved services.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
