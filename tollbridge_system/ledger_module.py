"""
Ledger Module: Immutable state management, transactional indices, 
and Write-Ahead Logging (WAL) state engine.
"""
import copy
import json
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LEDGER-ENGINE] %(levelname)s: %(message)s"
)
logger = logging.getLogger("ledger_engine")


class EnterpriseLedgerStore:
    def __init__(self, storage_file: str = "enterprise_ledger.wal"):
        self.storage_file = storage_file
        self.lock = threading.RLock()
        self.tables: Dict[str, Dict[str, Any]] = {
            "transactions": {},
            "nodes": {},
            "states": {},
            "metadata": {"initialized_at": time.time()}
        }
        self._wal_file = None
        self._sqlite_conn = None
        self._initialize_wal()
        logger.info("Enterprise Ledger Store initialized with persistent WAL: %s", self.storage_file)

    def _initialize_wal(self) -> None:
        with self.lock:
            # Replay existing WAL if file exists
            if os.path.exists(self.storage_file):
                self._replay_wal()

            parent_dir = os.path.dirname(self.storage_file)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            self._wal_file = open(self.storage_file, "a+", encoding="utf-8")

            # Enable WAL mode for SQLite
            import sqlite3
            self._sqlite_conn = sqlite3.connect(self.storage_file, isolation_level=None)
            self._sqlite_conn.execute("PRAGMA journal_mode=WAL;")
            self._sqlite_conn.close()

    def _replay_wal(self) -> None:
        entries_replayed = 0
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        op = record.get("op")
                        data = record.get("data", {})
                        if op == "commit_state":
                            key = data.get("key")
                            if key is not None:
                                self.tables["states"][key] = {
                                    "payload": data.get("payload"),
                                    "version": data.get("version", 1),
                                    "updated_at": data.get("timestamp", 0.0)
                                }
                                entries_replayed += 1
                        elif op == "log_transaction":
                            tx_id = data.get("tx_id")
                            if tx_id is not None:
                                self.tables["transactions"][tx_id] = {
                                    "status": data.get("status"),
                                    "details": data.get("details", {}),
                                    "timestamp": data.get("timestamp", 0.0)
                                }
                                entries_replayed += 1
                    except json.JSONDecodeError:
                        logger.warning("Corrupted WAL entry ignored at line %d in %s", line_num, self.storage_file)
            logger.info("Successfully replayed %d transactions/states from WAL.", entries_replayed)
        except OSError as e:
            logger.error("Failed to read WAL file %s: %s", self.storage_file, e)

    def _append_wal(self, operation: str, data: Dict[str, Any]) -> None:
        if self._wal_file is None:
            return
        entry = {
            "op": operation,
            "data": data,
            "recorded_at": time.time()
        }
        serialized = json.dumps(entry, separators=(",", ":"))
        self._wal_file.write(serialized + "\n")
        self._wal_file.flush()
        os.fsync(self._wal_file.fileno())

    def commit_state(self, key: str, value: Any) -> bool:
        if not isinstance(key, str) or not key:
            raise ValueError("State key must be a non-empty string.")
        with self.lock:
            version = self.tables["states"].get(key, {}).get("version", 0) + 1
            now = time.time()
            record_data = {
                "key": key,
                "payload": copy.deepcopy(value),
                "version": version,
                "timestamp": now
            }
            try:
                self._append_wal("commit_state", record_data)
            except Exception as e:
                logger.error("WAL append failed during commit_state for key '%s': %s", key, e)
                return False

            self.tables["states"][key] = {
                "payload": copy.deepcopy(value),
                "version": version,
                "updated_at": now
            }
            logger.info("Committed state update [Key: %s | Version: %d]", key, version)
            return True

    def get_state(self, key: str) -> Optional[Any]:
        with self.lock:
            record = self.tables["states"].get(key)
            if not record:
                return None
            return copy.deepcopy(record["payload"])

    def log_transaction(self, tx_id: str, status: str, details: dict) -> bool:
        if not isinstance(tx_id, str) or not tx_id:
            raise ValueError("Transaction ID must be a non-empty string.")
        if not isinstance(status, str):
            raise ValueError("Status must be a string.")
        if not isinstance(details, dict):
            raise ValueError("Details must be a dictionary.")

        with self.lock:
            now = time.time()
            record_data = {
                "tx_id": tx_id,
                "status": status,
                "details": copy.deepcopy(details),
                "timestamp": now
            }
            try:
                self._append_wal("log_transaction", record_data)
            except Exception as e:
                logger.error("WAL append failed during log_transaction for tx_id '%s': %s", tx_id, e)
                return False

            self.tables["transactions"][tx_id] = {
                "status": status,
                "details": copy.deepcopy(details),
                "timestamp": now
            }
            logger.info("Logged transaction [ID: %s | Status: %s]", tx_id, status)
            return True
