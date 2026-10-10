import os
import ast
import json
import time
import hashlib
import stat
import subprocess
import threading
from typing import Dict, List, Any, Tuple

TOPOLOGY_LEDGER = "sip_global_topology.json"

class SystemDuplicationError(Exception):
    """Raised when an operation attempts to overwrite an asset or duplicate AST symbols/hashes."""
    pass

class OmniCartographer:
    __slots__ = ('_watch_dir', '_lock', '_topology_state')

    def __init__(self, watch_dir: str = "."):
        self._watch_dir = watch_dir
        self._lock = threading.Lock()
        self._topology_state: Dict[str, Any] = {}

    def _safe_hash(self, filepath: str) -> str:
        """Reads files in 64KB chunks safely without mmap hanging."""
        try:
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "HASH_FAILED"

    def _extract_git_history(self) -> List[Dict[str, str]]:
        """Pulls git history safely without launching terminal pagers."""
        try:
            result = subprocess.run(
                ["git", "--no-pager", "log", "--pretty=format:%H|%an|%ad|%s", "--date=iso", "-n", "20"],
                capture_output=True, text=True, check=True, timeout=1, cwd=self._watch_dir
            )
            history = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        history.append({
                            "commit_hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            return history
        except Exception:
            return [{"warning": "Git ledger uninitialized or unreachable."}]

    def _parse_python_ast(self, filepath: str) -> Dict[str, List[str]]:
        """Extracts AST structure safely, handling sync and async methods."""
        classes, functions, raw_deps = [], [], []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                tree = ast.parse(f.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        raw_deps.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    raw_deps.append(node.module)
        except Exception:
            pass
        return {
            "classes": classes,
            "functions": functions,
            "dependencies": list(set(raw_deps))
        }

    def execute_mapping_cycle(self) -> Dict[str, Any]:
        """Runs mapping scan with kernel mode filtering to skip sockets and FIFOs."""
        system_inventory: Dict[str, Any] = {}

        for root, dirs, files in os.walk(self._watch_dir, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {"venv", "node_modules", "target", "build"}]

            for file in files:
                if file == TOPOLOGY_LEDGER or file.endswith(".tmp") or file.startswith('.'):
                    continue

                filepath = os.path.join(root, file)

                try:
                    st = os.lstat(filepath)

                    if not stat.S_ISREG(st.st_mode):
                        continue

                    file_ext = os.path.splitext(file)[1]

                    component_data = {
                        "path": filepath,
                        "size_bytes": st.st_size,
                        "last_modified_ts": st.st_mtime,
                        "sha256_hash": self._safe_hash(filepath),
                        "type": file_ext if file_ext else "binary_or_config"
                    }

                    if file_ext == ".py":
                        component_data.update(self._parse_python_ast(filepath))

                    system_inventory[filepath] = component_data
                except Exception:
                    continue

        with self._lock:
            self._topology_state = {
                "protocol": "Sovereign Intelligence Protocol",
                "mapping_timestamp": time.time(),
                "total_tracked_components": len(system_inventory),
                "historical_ledger": self._extract_git_history(),
                "system_components": system_inventory
            }

            temp_file = f"{TOPOLOGY_LEDGER}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._topology_state, f, indent=4)
            os.replace(temp_file, TOPOLOGY_LEDGER)

        return self._topology_state

    def validate_new_component(self, target_path: str, code_contents: str) -> Tuple[bool, str]:
        """Pre-flight check: Prevents overwriting files or duplicating classes/functions/hashes across workspace."""
        current_map = self.execute_mapping_cycle()["system_components"]

        # 1. Path Lock Check
        if os.path.exists(target_path):
            return False, f"PATH_LOCK_VIOLATION: File '{target_path}' already exists and is immutable."

        # 2. SHA-256 Byte Hash Check
        candidate_hash = hashlib.sha256(code_contents.encode('utf-8')).hexdigest()
        for path, meta in current_map.items():
            if meta.get("sha256_hash") == candidate_hash:
                return False, f"BYTE_DUPLICATION_VIOLATION: Identical payload already exists in '{path}'."

        # 3. AST Symbol Check (For Python components)
        if target_path.endswith(".py"):
            try:
                tree = ast.parse(code_contents)
                new_classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
                new_funcs = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

                for path, meta in current_map.items():
                    existing_classes = set(meta.get("classes", []))
                    existing_funcs = set(meta.get("functions", []))

                    class_clash = new_classes.intersection(existing_classes)
                    if class_clash:
                        return False, f"AST_SYMBOL_COLLISION: Class(es) {class_clash} already defined in '{path}'."

                    func_clash = new_funcs.intersection(existing_funcs)
                    if func_clash:
                        return False, f"AST_SYMBOL_COLLISION: Function(s) {func_clash} already defined in '{path}'."

            except SyntaxError as e:
                return False, f"SYNTAX_ERROR: Candidate code fails AST parsing: {str(e)}"

        return True, "VALIDATION_PASSED: Component is clean, distinct, and safe to deploy."

if __name__ == "__main__":
    mapper = OmniCartographer()
    report = mapper.execute_mapping_cycle()
    print(f"[*] Panopticon scan complete. Mapped {report['total_tracked_components']} components.")
    print(f"[*] Global topology ledger updated: {TOPOLOGY_LEDGER}")
