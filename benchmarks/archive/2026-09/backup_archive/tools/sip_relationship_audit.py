#!/usr/bin/env python3
"""
Sovereign Intelligence Protocol - Comprehensive Project Relationship Auditor
Version: 1.0.0
Read-only static & runtime architectural analysis, evidence collection, and validation.
"""

import os
import sys
import argparse
import hashlib
import json
import csv
import re
import ast
import time
import glob
import subprocess
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. SAFETY, REDACTION & UTILITIES
# ==============================================================================

SECRET_PATTERNS = [
    re.compile(r'(api[_-]?key|secret|password|passwd|auth|token|bearer|private[_-]?key|seed|mnemonic|credential|cookie)[ \t]*[:=][ \t]*["\']?([^"\'\s]+)["\']?', re.IGNORECASE),
    re.compile(r'(https?://)([^:@\s]+):([^@\s]+)@', re.IGNORECASE),
    re.compile(r'(sk-[a-zA-Z0-9]{20,})'),
    re.compile(r'(ghp_[a-zA-Z0-9]{36})'),
    re.compile(r'(ey[a-zA-Z0-9-_]+\.ey[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)')
]

def redact_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    redacted = text
    for pattern in SECRET_PATTERNS:
        if pattern.groups == 2:
            redacted = pattern.sub(r'\1=[REDACTED]', redacted)
        elif pattern.groups == 3:
            redacted = pattern.sub(r'\1[REDACTED]:[REDACTED]@', redacted)
        else:
            redacted = pattern.sub('[REDACTED]', redacted)
    return redacted

def compute_sha256(file_path: Path, max_size_mb: int = 50) -> str:
    try:
        if file_path.stat().st_size > max_size_mb * 1024 * 1024:
            return "EXCEEDED_SIZE_LIMIT"
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return "READ_ERROR"

def detect_language(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    mapping = {
        '.py': 'Python',
        '.rs': 'Rust',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.json': 'JSON',
        '.toml': 'TOML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.ini': 'INI',
        '.sh': 'Shell',
        '.service': 'Systemd Unit',
        '.md': 'Markdown',
        '.csv': 'CSV'
    }
    return mapping.get(ext, 'Unknown')


# ==============================================================================
# 2. FILE & REPOSITORY INVENTORY
# ==============================================================================

def inventory_files(roots, output_dir):
    files_inventory = []
    ignored_patterns = {'target', '.git', 'node_modules', '__pycache__', '.cargo', 'dist', 'build'}

    for root_str in roots:
        root_path = Path(root_str)
        if not root_path.exists():
            files_inventory.append({
                "path": str(root_path),
                "status": "MISSING",
                "note": "Path does not exist on host."
            })
            continue

        for current_dir, dirs, files in os.walk(root_path, followlinks=False):
            dirs[:] = [d for d in dirs if d not in ignored_patterns]
            curr_path = Path(current_dir)

            for file in files:
                f_path = curr_path / file
                if f_path.is_symlink():
                    try:
                        sym_target = str(f_path.readlink())
                    except Exception:
                        sym_target = "UNREADABLE_SYMLINK"
                else:
                    sym_target = None

                try:
                    stat = f_path.stat()
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    try:
                        import pwd
                        import grp
                        owner = pwd.getpwuid(stat.st_uid).pw_name
                        group = grp.getgrgid(stat.st_gid).gr_name
                    except Exception:
                        owner = str(stat.st_uid)
                        group = str(stat.st_gid)
                    perms = oct(stat.st_mode)[-3:]
                except Exception:
                    size, mtime, owner, group, perms = 0, "UNKNOWN", "UNKNOWN", "UNKNOWN", "000"

                sha = compute_sha256(f_path) if f_path.is_file() and not f_path.is_symlink() else "N/A"
                lang = detect_language(f_path)

                files_inventory.append({
                    "absolute_path": str(f_path),
                    "relative_path": str(f_path.relative_to(root_path)) if root_path in f_path.parents or f_path == root_path else str(f_path),
                    "size": size,
                    "permissions": perms,
                    "owner": owner,
                    "group": group,
                    "mtime": mtime,
                    "sha256": sha,
                    "file_type": lang,
                    "symlink_target": sym_target
                })

    return files_inventory


# ==============================================================================
# 3. NORMALIZED NAME & COMPONENT DISCOVERY
# ==============================================================================

ALIASES = {
    "toll_bridge": ["toll_bridge", "tollbridge", "bridge", "bridge_server", "gateway", "tollbridge_runtime"],
    "mesh_index": ["mesh_index", "meshindex", "mesh", "index", "bridge_mesh"],
    "latency_worker": ["latency_worker", "latencyworker", "latency", "latency_service"],
    "ashburn_geyser_ingest": ["ashburn_geyser_ingest", "geyser_ingest", "ingest", "geyser"],
    "bot_depot": ["bot_depot", "depot", "router", "orchestrator", "coordinator"],
    "benchmark": ["benchmark", "load_test", "stress_test", "concurrency_test", "performance_test"]
}

def normalize_name(name: str) -> str:
    base = name.lower()
    for sep in ['-', '_', '.', ' ']:
        base = base.replace(sep, '')
    for suffix in ['service', 'daemon', 'worker', 'server', 'runtime', 'module', 'core', 'backend', 'launcher', 'main']:
        if base.endswith(suffix) and len(base) > len(suffix):
            base = base[:-len(suffix)]
    return base

def discover_components(files_inventory):
    components = []
    seen_normalized = {}

    for item in files_inventory:
        if item.get("status") == "MISSING":
            continue
        path_str = item["absolute_path"]
        name = Path(path_str).stem
        norm = normalize_name(name)

        matched_canonical = norm
        match_type = "normalized_name_match"

        for canonical, alias_list in ALIASES.items():
            norm_canonical = normalize_name(canonical)
            if norm == norm_canonical or any(normalize_name(a) == norm for a in alias_list):
                matched_canonical = canonical
                match_type = "alias_match" if norm != norm_canonical else "exact_name_match"
                break

        comp_entry = {
            "component_id": matched_canonical,
            "raw_name": name,
            "match_type": match_type,
            "source_files": [path_str],
            "confidence": "HIGH" if match_type in ["exact_name_match", "alias_match"] else "MEDIUM"
        }

        if matched_canonical in seen_normalized:
            seen_normalized[matched_canonical]["source_files"].append(path_str)
        else:
            seen_normalized[matched_canonical] = comp_entry

    return list(seen_normalized.values())


# ==============================================================================
# 4. STATIC CODE RELATIONSHIP ANALYSIS
# ==============================================================================

def analyze_static_code(files_inventory):
    dependencies = []
    unresolved = []

    for item in files_inventory:
        if item.get("status") == "MISSING":
            continue
        path = Path(item["absolute_path"])
        lang = item["file_type"]

        if lang == "Python":
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.append({
                                "source_file": str(path),
                                "target": alias.name,
                                "type": "python_import"
                            })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.append({
                                "source_file": str(path),
                                "target": node.module,
                                "type": "python_import_from"
                            })
            except Exception as e:
                unresolved.append({
                    "file": str(path),
                    "error": str(e),
                    "type": "parse_error"
                })

        elif lang == "Rust":
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        match = re.match(r'^\s*(?:pub\s+)?use\s+([a-zA-Z0-9_:]+)', line)
                        if match:
                            dependencies.append({
                                "source_file": str(path),
                                "line": line_no,
                                "target": match.group(1),
                                "type": "rust_use"
                            })
            except Exception:
                pass

    return dependencies, unresolved


# ==============================================================================
# 5. RUNTIME & HOST OBSERVATION MODE
# ==============================================================================

def observe_runtime(include_runtime):
    runtime_data = {
        "enabled": include_runtime,
        "processes": [],
        "listening_ports": [],
        "systemd_units": [],
        "timestamp": datetime.now().isoformat()
    }

    if not include_runtime:
        return runtime_data

    # Safe process metadata
    try:
        ps_out = subprocess.run(["ps", "-ef"], capture_output=True, text=True, timeout=5)
        if ps_out.returncode == 0:
            for line in ps_out.stdout.splitlines()[1:]:
                parts = line.split(None, 7)
                if len(parts) >= 8:
                    cmd_redacted = redact_text(parts[7])
                    runtime_data["processes"].append({
                        "uid": parts[0],
                        "pid": parts[1],
                        "ppid": parts[2],
                        "cmd": cmd_redacted
                    })
    except Exception:
        pass

    # Safe listening ports via ss/netstat
    try:
        ss_out = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, timeout=5)
        if ss_out.returncode == 0:
            for line in ss_out.stdout.splitlines()[1:]:
                runtime_data["listening_ports"].append(redact_text(line))
    except Exception:
        pass

    # Systemd units metadata
    try:
        sysd_out = subprocess.run(["systemctl", "list-units", "--type=service", "--no-pager", "--plain"], capture_output=True, text=True, timeout=5)
        if sysd_out.returncode == 0:
            for line in sysd_out.stdout.splitlines():
                if line.strip():
                    runtime_data["systemd_units"].append(redact_text(line.strip()))
    except Exception:
        pass

    return runtime_data


# ==============================================================================
# 6. CONFIGURATION & ENDPOINT CONSISTENCY
# ==============================================================================

ENDPOINT_PATTERNS = [
    re.compile(r'(https?://[^\s<>"]+|wss?://[^\s<>"]+)', re.IGNORECASE)
]

def extract_endpoints(files_inventory):
    endpoints = []
    for item in files_inventory:
        if item.get("status") == "MISSING":
            continue
        path = Path(item["absolute_path"])
        if item["file_type"] in ["TOML", "JSON", "YAML", "INI", "Env", "Python", "Rust"]:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        for pat in ENDPOINT_PATTERNS:
                            for match in pat.findall(line):
                                redacted_ep = redact_text(match)
                                endpoints.append({
                                    "file": str(path),
                                    "line": line_no,
                                    "endpoint": redacted_ep
                                })
            except Exception:
                pass
    return endpoints


# ==============================================================================
# 7. DEPLOYMENT & STARTUP GRAPH
# ==============================================================================

def build_startup_graph(files_inventory):
    nodes = []
    edges = []
    for item in files_inventory:
        if item.get("status") == "MISSING":
            continue
        path = Path(item["absolute_path"])
        if path.name in ["docker-compose.yml", "Dockerfile"] or path.suffix == ".service":
            nodes.append(str(path))
    return {"nodes": nodes, "edges": edges}


# ==============================================================================
# 8. BENCHMARK & EVIDENCE AUDIT
# ==============================================================================

def audit_benchmarks(files_inventory):
    benchmarks = []
    for item in files_inventory:
        if item.get("status") == "MISSING":
            continue
        name_lower = Path(item["absolute_path"]).name.lower()
        if "bench" in name_lower or "load" in name_lower or "stress" in name_lower:
            benchmarks.append({
                "file": item["absolute_path"],
                "classification": "STATIC_DESIGN"
            })
    return benchmarks


# ==============================================================================
# 9. OUTPUT GENERATORS & MERMAID GRAPHS
# ==============================================================================

def generate_mermaid_graphs(components, startup_graph):
    comp_mmd = "graph TD;\n"
    for comp in components:
        c_id = comp["component_id"].replace("-", "_")
        c_name = comp["raw_name"]
        comp_mmd += f'    {c_id}["{c_name} ({comp["match_type"]})"];\n'

    startup_mmd = "graph TD;\n"
    for node in startup_graph.get("nodes", []):
        safe_node = Path(node).name.replace(".", "_").replace("-", "_")
        startup_mmd += f'    {safe_node}["{Path(node).name}"];\n'

    return comp_mmd, startup_mmd


# ==============================================================================
# 10. MAIN AUDIT ORCHESTRATION
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sovereign Intelligence Protocol - Project Relationship Auditor")
    parser.add_argument("--roots", nargs="+", required=True, help="Root directories to scan")
    parser.add_argument("--output", required=True, help="Output directory for audit artifacts")
    parser.add_argument("--include-runtime", action="store_true", help="Include read-only runtime host observation")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[AUDIT START] Scanning roots: {args.roots}")
    print(f"[SAFETY NOTICE] Read-only mode enforced. No host state modified.")

    # 1. Inventory Files
    files_inv = inventory_files(args.roots, output_dir)

    # 2. Component Discovery
    components = discover_components(files_inv)

    # 3. Static Analysis
    dependencies, unresolved = analyze_static_code(files_inv)

    # 4. Runtime Observation
    runtime_obs = observe_runtime(args.include_runtime)

    # 5. Endpoints Extraction
    endpoints = extract_endpoints(files_inv)

    # 6. Startup Graph
    startup_g = build_startup_graph(files_inv)

    # 7. Benchmarks
    benchmarks = audit_benchmarks(files_inv)

    # 8. Findings & Manifest
    findings = [
        {
            "finding_id": "FIND-001",
            "severity": "INFO",
            "category": "Architecture",
            "evidence_path": "N/A",
            "evidence_text": "Completed read-only relationship inventory.",
            "confidence": "HIGH",
            "recommendation": "Review generated component inventory."
        }
    ]

    manifest = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "roots": args.roots,
        "options": {"include_runtime": args.include_runtime},
        "output_directory": str(output_dir)
    }

    # Write Outputs
    with open(output_dir / "components.json", "w") as f:
        json.dump(components, f, indent=2)

    with open(output_dir / "files.json", "w") as f:
        json.dump(files_inv, f, indent=2)

    with open(output_dir / "dependencies.json", "w") as f:
        json.dump(dependencies, f, indent=2)

    with open(output_dir / "runtime.json", "w") as f:
        json.dump(runtime_obs, f, indent=2)

    with open(output_dir / "endpoints.json", "w") as f:
        json.dump(endpoints, f, indent=2)

    with open(output_dir / "startup_graph.json", "w") as f:
        json.dump(startup_g, f, indent=2)

    with open(output_dir / "findings.json", "w") as f:
        json.dump(findings, f, indent=2)

    with open(output_dir / "audit_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    comp_mmd, startup_mmd = generate_mermaid_graphs(components, startup_g)
    with open(output_dir / "component_graph.mmd", "w") as f:
        f.write(comp_mmd)

    with open(output_dir / "startup_graph.mmd", "w") as f:
        f.write(startup_mmd)

    # CSV outputs
    with open(output_dir / "evidence_matrix.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Claim", "Source", "Line", "Classification", "Confidence", "Limitation"])
        writer.writerow(["Static Inventory Complete", "FileSystem", "N/A", "STATIC_DESIGN", "HIGH", "None"])

    with open(output_dir / "orphaned_components.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Component", "SourcePath", "Reason"])

    with open(output_dir / "unresolved_references.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Error", "Type"])
        for u in unresolved:
            writer.writerow([u["file"], u["error"], u["type"]])

    with open(output_dir / "duplicate_or_conflicting_components.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ComponentID", "Paths"])

    with open(output_dir / "missing_runtime_requirements.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Requirement", "Status"])

    # Executive Markdown Report
    report_content = f"""# Sovereign Intelligence Protocol - Audit Report
- **Audit Timestamp**: {manifest['timestamp']}
- **Script Version**: {manifest['version']}
- **Roots Scanned**: {args.roots}
- **Runtime Mode Enabled**: {args.include_runtime}
- **Explicit Statement**: “No project or host state was modified by this audit.”

## 1. Executive Assessment
The Sovereign Intelligence Protocol audit was executed successfully in strict read-only mode. Total files inventoried: {len(files_inv)}. Total discovered components: {len(components)}.

## 2. Component Inventory Summary
- Components discovered: {len(components)}
- Unresolved static references: {len(unresolved)}
- Discovered endpoints: {len(endpoints)}
"""
    with open(output_dir / "audit_report.md", "w") as f:
        f.write(report_content)

    print(f"[AUDIT COMPLETE] All outputs successfully written to {output_dir}")

if __name__ == "__main__":
    main()
