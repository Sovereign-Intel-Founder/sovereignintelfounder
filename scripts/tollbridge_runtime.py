#!/usr/bin/env python3
"""Tollbridge local pipeline runtime.

This process has three roles: gateway, worker, and mesh.  It uses the host's
Redis service for durable hand-off, SQLite for durable local state, and Reth
only for read-only chain verification.  It never signs or broadcasts a
transaction.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import hmac
import http.client
import json
import logging
import os
import signal
import socket
import sqlite3
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterable
from urllib.parse import urlparse
from quota_gate import QuotaGate

LOG = logging.getLogger("tollbridge")
STOP = threading.Event()


@dataclass(frozen=True)
class Settings:
    base_dir: str
    database_path: str
    mesh_config_path: str
    redis_host: str
    redis_port: int
    redis_stream: str
    redis_group: str
    reth_url: str
    bridge_host: str
    bridge_port: int
    ingress_secret: str
    max_payload_bytes: int
    max_concurrent_requests: int
    request_timeout_seconds: float
    node_ttl_seconds: int

    @classmethod
    def load(cls) -> "Settings":
        base = os.environ.get("TOLLBRIDGE_BASE_DIR", "/opt/tollbridge_system")
        secret = os.environ.get("TOLLBRIDGE_INGRESS_SECRET", "")
        if not secret:
            secret_path = os.environ.get("TOLLBRIDGE_INGRESS_SECRET_FILE", os.path.join(base, ".ingress_secret"))
            try:
                with open(secret_path, "r", encoding="utf-8") as secret_file:
                    secret = secret_file.read().strip()
            except OSError as exc:
                raise RuntimeError(f"unable to load ingress secret: {exc}") from exc
        if len(secret) < 32:
            raise RuntimeError("ingress secret must contain at least 32 characters")
        return cls(
            base_dir=base,
            database_path=os.environ.get("TOLLBRIDGE_DATABASE", os.path.join(base, "toll_bridge.db")),
            mesh_config_path=os.environ.get("TOLLBRIDGE_MESH_CONFIG", os.path.join(base, "bridge_mesh.json")),
            redis_host=os.environ.get("TOLLBRIDGE_REDIS_HOST", "127.0.0.1"),
            redis_port=int(os.environ.get("TOLLBRIDGE_REDIS_PORT", "6379")),
            redis_stream=os.environ.get("TOLLBRIDGE_REDIS_STREAM", "tollbridge:events"),
            redis_group=os.environ.get("TOLLBRIDGE_REDIS_GROUP", "tollbridge-workers"),
            reth_url=os.environ.get("TOLLBRIDGE_RETH_URL", "http://127.0.0.1:8545"),
            bridge_host=os.environ.get("TOLLBRIDGE_BRIDGE_HOST", "127.0.0.1"),
            bridge_port=int(os.environ.get("TOLLBRIDGE_BRIDGE_PORT", "8080")),
            ingress_secret=secret,
            max_payload_bytes=int(os.environ.get("TOLLBRIDGE_MAX_PAYLOAD_BYTES", "1048576")),
            max_concurrent_requests=int(os.environ.get("TOLLBRIDGE_MAX_CONCURRENT_REQUESTS", "64")),
            request_timeout_seconds=float(os.environ.get("TOLLBRIDGE_REQUEST_TIMEOUT_SECONDS", "10")),
            node_ttl_seconds=int(os.environ.get("TOLLBRIDGE_NODE_TTL_SECONDS", "30")),
        )


class RedisError(RuntimeError):
    pass


class RedisClient:
    """Small RESP client used to avoid an undeclared third-party dependency."""

    def __init__(self, host: str, port: int, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    @staticmethod
    def _encode(parts: Iterable[Any]) -> bytes:
        encoded = []
        normalized = []
        for item in parts:
            value = item if isinstance(item, bytes) else str(item).encode("utf-8")
            normalized.append(value)
        encoded.append(f"*{len(normalized)}\r\n".encode("ascii"))
        for value in normalized:
            encoded.append(f"${len(value)}\r\n".encode("ascii"))
            encoded.append(value + b"\r\n")
        return b"".join(encoded)

    @staticmethod
    def _read_line(reader: Any) -> bytes:
        line = reader.readline()
        if not line.endswith(b"\r\n"):
            raise RedisError("truncated Redis response")
        return line[:-2]

    @classmethod
    def _read_reply(cls, reader: Any) -> Any:
        prefix = reader.read(1)
        if not prefix:
            raise RedisError("empty Redis response")
        line = cls._read_line(reader)
        if prefix == b"+":
            return line.decode("utf-8")
        if prefix == b"-":
            raise RedisError(line.decode("utf-8", errors="replace"))
        if prefix == b":":
            return int(line)
        if prefix == b"$":
            size = int(line)
            if size == -1:
                return None
            value = reader.read(size)
            if len(value) != size or reader.read(2) != b"\r\n":
                raise RedisError("truncated Redis bulk response")
            return value.decode("utf-8", errors="replace")
        if prefix == b"*":
            count = int(line)
            if count == -1:
                return None
            return [cls._read_reply(reader) for _ in range(count)]
        raise RedisError("unknown Redis response type")

    def execute(self, *parts: Any) -> Any:
        try:
            with socket.create_connection((self.host, self.port), self.timeout) as connection:
                connection.settimeout(self.timeout)
                writer = connection.makefile("wb")
                reader = connection.makefile("rb")
                writer.write(self._encode(parts))
                writer.flush()
                return self._read_reply(reader)
        except OSError as exc:
            raise RedisError(f"Redis transport failure: {exc}") from exc

    def ping(self) -> bool:
        return self.execute("PING") == "PONG"

    def xadd(self, stream: str, fields: dict[str, str]) -> str:
        command: list[Any] = ["XADD", stream, "*"]
        for key, value in fields.items():
            command.extend([key, value])
        result = self.execute(*command)
        if not isinstance(result, str):
            raise RedisError("Redis did not return a stream message id")
        return result

    def ensure_group(self, stream: str, group: str) -> None:
        try:
            self.execute("XGROUP", "CREATE", stream, group, "0", "MKSTREAM")
        except RedisError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def xreadgroup(self, stream: str, group: str, consumer: str, count: int = 16, block_ms: int = 1000) -> list[tuple[str, dict[str, str]]]:
        result = self.execute("XREADGROUP", "GROUP", group, consumer, "COUNT", count, "BLOCK", block_ms, "STREAMS", stream, ">")
        messages: list[tuple[str, dict[str, str]]] = []
        if not result:
            return messages
        for stream_record in result:
            if not isinstance(stream_record, list) or len(stream_record) != 2:
                continue
            records = stream_record[1]
            for record in records or []:
                if not isinstance(record, list) or len(record) != 2:
                    continue
                message_id, flat_fields = record
                fields: dict[str, str] = {}
                for index in range(0, len(flat_fields or []), 2):
                    fields[str(flat_fields[index])] = str(flat_fields[index + 1])
                messages.append((str(message_id), fields))
        return messages

    def xack(self, stream: str, group: str, message_id: str) -> None:
        self.execute("XACK", stream, group, message_id)

    def hset(self, key: str, mapping: dict[str, str]) -> None:
        command: list[Any] = ["HSET", key]
        for field, value in mapping.items():
            command.extend([field, value])
        self.execute(*command)

    def expire(self, key: str, seconds: int) -> None:
        self.execute("EXPIRE", key, seconds)


class Ledger:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.RLock()

    @contextmanager
    def connection(self) -> Any:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA busy_timeout=10000")
            yield connection
        finally:
            connection.close()

    def migrate(self) -> None:
        with self._lock, self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS pipeline_events (
                    event_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    stream_id TEXT,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    chain_status TEXT,
                    chain_tx_hash TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_pipeline_events_status ON pipeline_events(status, updated_at);
                CREATE INDEX IF NOT EXISTS idx_pipeline_events_digest ON pipeline_events(payload_digest);
                CREATE TABLE IF NOT EXISTS mesh_nodes (
                    node_id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_heartbeat TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    details_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_mesh_nodes_status ON mesh_nodes(status, last_heartbeat);
                """
            )

    def enqueue(self, event_id: str, source: str, payload_json: str, digest: str) -> bool:
        with self._lock, self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                cursor = connection.execute(
                    "INSERT OR IGNORE INTO pipeline_events(event_id, source, payload_json, payload_digest, status) VALUES (?, ?, ?, ?, 'queued')",
                    (event_id, source, payload_json, digest),
                )
                connection.execute("COMMIT")
                return cursor.rowcount == 1
            except Exception:
                connection.execute("ROLLBACK")
                raise

    def set_stream_id(self, event_id: str, stream_id: str) -> None:
        with self._lock, self.connection() as connection:
            connection.execute("UPDATE pipeline_events SET stream_id=?, updated_at=CURRENT_TIMESTAMP WHERE event_id=?", (stream_id, event_id))

    def mark_processing(self, event_id: str) -> None:
        with self._lock, self.connection() as connection:
            connection.execute("UPDATE pipeline_events SET status='processing', attempts=attempts+1, updated_at=CURRENT_TIMESTAMP WHERE event_id=?", (event_id,))

    def mark_complete(self, event_id: str, chain_status: str) -> None:
        with self._lock, self.connection() as connection:
            connection.execute("UPDATE pipeline_events SET status='completed', chain_status=?, error_message=NULL, updated_at=CURRENT_TIMESTAMP WHERE event_id=?", (chain_status, event_id))

    def mark_failed(self, event_id: str, error: str) -> None:
        with self._lock, self.connection() as connection:
            connection.execute("UPDATE pipeline_events SET status='failed', error_message=?, updated_at=CURRENT_TIMESTAMP WHERE event_id=?", (error[:1000], event_id))

    def heartbeat(self, node_id: str, role: str, details: dict[str, Any]) -> None:
        details_json = json.dumps(details, sort_keys=True, separators=(",", ":"))
        with self._lock, self.connection() as connection:
            connection.execute(
                """INSERT INTO mesh_nodes(node_id, role, status, last_heartbeat, details_json)
                VALUES (?, ?, 'healthy', CURRENT_TIMESTAMP, ?)
                ON CONFLICT(node_id) DO UPDATE SET role=excluded.role, status='healthy', last_heartbeat=CURRENT_TIMESTAMP, details_json=excluded.details_json""",
                (node_id, role, details_json),
            )

    def health(self) -> dict[str, Any]:
        with self._lock, self.connection() as connection:
            pending = connection.execute("SELECT COUNT(*) FROM pipeline_events WHERE status IN ('queued','processing')").fetchone()[0]
            failed = connection.execute("SELECT COUNT(*) FROM pipeline_events WHERE status='failed'").fetchone()[0]
            completed = connection.execute("SELECT COUNT(*) FROM pipeline_events WHERE status='completed'").fetchone()[0]
        return {"queued_or_processing": pending, "failed": failed, "completed": completed}


class RethVerifier:
    def __init__(self, url: str, timeout: float = 4.0):
        parsed = urlparse(url)
        if parsed.scheme != "http" or not parsed.hostname:
            raise RuntimeError("TOLLBRIDGE_RETH_URL must be an http JSON-RPC endpoint")
        self.host = parsed.hostname
        self.port = parsed.port or 80
        self.path = parsed.path or "/"
        self.timeout = timeout

    def call(self, method: str, params: list[Any]) -> Any:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
        connection = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        try:
            connection.request("POST", self.path, body=body, headers={"Content-Type": "application/json", "Content-Length": str(len(body))})
            response = connection.getresponse()
            data = response.read()
            if response.status != 200:
                raise RuntimeError(f"Reth returned HTTP {response.status}")
            decoded = json.loads(data.decode("utf-8"))
            if decoded.get("error"):
                raise RuntimeError(f"Reth JSON-RPC error: {decoded['error']}")
            return decoded.get("result")
        finally:
            connection.close()

    def chain_id(self) -> str:
        result = self.call("eth_chainId", [])
        if not isinstance(result, str):
            raise RuntimeError("Reth did not return an EVM chain id")
        return result

    def verify_event(self, payload: dict[str, Any]) -> str:
        tx_hash = payload.get("chain_tx_hash")
        if not tx_hash:
            return f"reth_chain:{self.chain_id()}"
        if not isinstance(tx_hash, str) or not tx_hash.startswith("0x"):
            raise ValueError("chain_tx_hash must be an EVM hexadecimal transaction hash")
        receipt = self.call("eth_getTransactionReceipt", [tx_hash])
        return "reth_receipt_confirmed" if receipt else "reth_receipt_pending"


class Pipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis = RedisClient(settings.redis_host, settings.redis_port)
        self.ledger = Ledger(settings.database_path)
        self.reth = RethVerifier(settings.reth_url)
        self.mesh_config: dict[str, Any] = {}

    def load_mesh_config(self) -> None:
        try:
            with open(self.settings.mesh_config_path, "r", encoding="utf-8") as mesh_file:
                config = json.load(mesh_file)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"invalid mesh configuration: {exc}") from exc
        if not isinstance(config, dict):
            raise RuntimeError("mesh configuration must be a JSON object")
        core_bridge = config.get("core_bridge")
        durable_state = config.get("durable_state")
        ingress = config.get("ingress")
        routing = config.get("routing")
        if config.get("node_mode") != "non_voting_bridge":
            raise RuntimeError("mesh configuration must define a non_voting_bridge node")
        if not isinstance(core_bridge, dict) or core_bridge.get("bind_host") != self.settings.bridge_host or core_bridge.get("bind_port") != self.settings.bridge_port:
            raise RuntimeError("mesh core bridge binding does not match runtime binding")
        if not isinstance(durable_state, dict) or not isinstance(durable_state.get("event_stream"), dict):
            raise RuntimeError("mesh configuration lacks durable event stream settings")
        event_stream = durable_state["event_stream"]
        if event_stream.get("host") != self.settings.redis_host or event_stream.get("port") != self.settings.redis_port or event_stream.get("stream") != self.settings.redis_stream or event_stream.get("consumer_group") != self.settings.redis_group:
            raise RuntimeError("mesh event stream settings do not match runtime settings")
        if not isinstance(ingress, dict) or ingress.get("authentication") != "hmac_sha256":
            raise RuntimeError("mesh ingress must use hmac_sha256 authentication")
        if not isinstance(routing, dict) or routing.get("financial_broadcast_enabled") is not False:
            raise RuntimeError("local raw-ingest mode prohibits financial broadcast")
        self.mesh_config = config

    def initialize(self) -> None:
        os.makedirs(self.settings.base_dir, exist_ok=True)
        self.load_mesh_config()
        self.ledger.migrate()
        if not self.redis.ping():
            raise RuntimeError("Redis health check failed")
        self.redis.ensure_group(self.settings.redis_stream, self.settings.redis_group)
        self.reth.chain_id()

    def health(self) -> dict[str, Any]:
        redis_ok = self.redis.ping()
        chain_id = self.reth.chain_id()
        return {"redis": redis_ok, "reth_chain_id": chain_id, "ledger": self.ledger.health(), "mesh": {"node_mode": self.mesh_config.get("node_mode"), "routing_mode": self.mesh_config.get("routing", {}).get("mode"), "financial_broadcast_enabled": self.mesh_config.get("routing", {}).get("financial_broadcast_enabled")}}

    def ingest(self, payload: dict[str, Any], source: str) -> tuple[str, bool]:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        event_id = str(payload.get("event_id") or digest)
        inserted = self.ledger.enqueue(event_id, source, canonical, digest)
        if not inserted:
            return event_id, False
        try:
            stream_id = self.redis.xadd(self.settings.redis_stream, {"event_id": event_id, "source": source, "payload": canonical})
            self.ledger.set_stream_id(event_id, stream_id)
            return event_id, True
        except Exception as exc:
            self.ledger.mark_failed(event_id, f"enqueue failed: {exc}")
            raise

    def process_once(self, consumer: str) -> int:
        processed = 0
        for message_id, fields in self.redis.xreadgroup(self.settings.redis_stream, self.settings.redis_group, consumer):
            event_id = fields.get("event_id")
            if not event_id or "payload" not in fields:
                LOG.error("Rejecting malformed Redis message %s", message_id)
                self.redis.xack(self.settings.redis_stream, self.settings.redis_group, message_id)
                continue
            try:
                payload = json.loads(fields["payload"])
                if not isinstance(payload, dict):
                    raise ValueError("event payload must be an object")
                self.ledger.mark_processing(event_id)
                chain_status = self.reth.verify_event(payload)
                self.ledger.mark_complete(event_id, chain_status)
                self.redis.xack(self.settings.redis_stream, self.settings.redis_group, message_id)
                processed += 1
            except Exception as exc:
                LOG.exception("Worker error for event %s", event_id)
                self.ledger.mark_failed(event_id, str(exc))
                # Keep the message pending for explicit recovery instead of silently discarding it.
        return processed

    def heartbeat(self, node_id: str, role: str) -> None:
        details = {"pid": os.getpid(), "host": socket.gethostname(), "role": role, "timestamp": int(time.time())}
        self.redis.hset(f"tollbridge:mesh:{node_id}", {key: str(value) for key, value in details.items()})
        self.redis.expire(f"tollbridge:mesh:{node_id}", self.settings.node_ttl_seconds)
        self.ledger.heartbeat(node_id, role, details)


class CoreBridgeServer(ThreadingHTTPServer):
    request_queue_size = 64
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler], max_inflight: int, request_timeout: float):
        if max_inflight < 1:
            raise ValueError("TOLLBRIDGE_MAX_CONCURRENT_REQUESTS must be positive")
        if request_timeout <= 0:
            raise ValueError("TOLLBRIDGE_REQUEST_TIMEOUT_SECONDS must be positive")
        self._request_slots = threading.BoundedSemaphore(max_inflight)
        self._request_timeout = request_timeout
        super().__init__(server_address, handler_class)

    def get_request(self) -> tuple[socket.socket, tuple[str, int]]:
        request, client_address = super().get_request()
        request.settimeout(self._request_timeout)
        return request, client_address

    def process_request(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        if not self._request_slots.acquire(blocking=False):
            try:
                request.sendall(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            except OSError:
                pass
            finally:
                request.close()
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._request_slots.release()
            raise

    def process_request_thread(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._request_slots.release()


class TollBridgeHandler(BaseHTTPRequestHandler):
    pipeline: Pipeline
    quota_gate: QuotaGate
    request_times: dict[str, deque[float]] = {}
    request_times_lock = threading.Lock()
    rate_window_seconds = 10.0
    max_requests_per_window = 10000

    server_version = "TollbridgeCoreBridge/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        # Rejected traffic can be high-volume; error details are logged at decision points instead.
        return

    def _within_rate_limit(self) -> bool:
        now = time.monotonic()
        client = self.client_address[0]
        with self.request_times_lock:
            window = self.request_times.setdefault(client, deque())
            cutoff = now - self.rate_window_seconds
            while window and window[0] < cutoff:
                window.popleft()
            if len(window) >= self.max_requests_per_window:
                return False
            window.append(now)
            return True

    def _respond(self, status: HTTPStatus, payload: dict[str, Any], *, close: bool = False) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close" if close else "keep-alive")
        self.end_headers()
        self.wfile.write(body)
        if close:
            self.close_connection = True

    def _is_authenticated(self, body: bytes) -> bool:
        provided = self.headers.get("X-Tollbridge-Signature", "")
        expected = hmac.new(self.pipeline.settings.ingress_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        if provided.startswith("sha256="):
            provided = provided[7:]
        return bool(provided) and hmac.compare_digest(provided, expected)

    def do_GET(self) -> None:
        if not self._within_rate_limit():
            self._respond(HTTPStatus.TOO_MANY_REQUESTS, {"error": "rate limit exceeded"}, close=True)
            return
        if self.path == "/health":
            try:
                self._respond(HTTPStatus.OK, {"status": "operational", "services": self.pipeline.health()})
            except Exception as exc:
                LOG.exception("health probe failed")
                self._respond(HTTPStatus.SERVICE_UNAVAILABLE, {"status": "degraded", "error": str(exc)})
            return
        self._respond(HTTPStatus.NOT_FOUND, {"error": "not found"}, close=True)

    def do_POST(self) -> None:
        if not self._within_rate_limit():
            self._respond(HTTPStatus.TOO_MANY_REQUESTS, {"error": "rate limit exceeded"}, close=True)
            return
        if self.path != "/v1/ingress/raw":
            self._respond(HTTPStatus.NOT_FOUND, {"error": "not found"}, close=True)
            return
        length_text = self.headers.get("Content-Length")
        try:
            content_length = int(length_text or "-1")
        except ValueError:
            content_length = -1
        if content_length < 1 or content_length > self.pipeline.settings.max_payload_bytes:
            self._respond(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "invalid payload length"}, close=True)
            return
        body = self.rfile.read(content_length)
        if not self._is_authenticated(body):
            self._respond(HTTPStatus.UNAUTHORIZED, {"error": "invalid signature"})
            return
        try:
            payload = json.loads(body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON payload must be an object")
            client_identifier = (
                self.headers.get("X-Client-Token")
                or self.headers.get("X-Client-Signature")
                or self.headers.get("X-Tollbridge-Client")
                or self.client_address[0]
            )[:512]
            allowed, uses = self.quota_gate.reserve(client_identifier)
            if not allowed:
                self._respond(HTTPStatus.PAYMENT_REQUIRED, self.quota_gate.challenge(uses), close=True)
                return
            source = self.headers.get("X-Tollbridge-Source", "local")[:128]
            event_id, accepted = self.pipeline.ingest(payload, source)
            status = HTTPStatus.ACCEPTED if accepted else HTTPStatus.OK
            self._respond(status, {"event_id": event_id, "status": "queued" if accepted else "duplicate"})
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._respond(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            LOG.exception("ingress failure")
            self._respond(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "pipeline unavailable", "detail": str(exc)})


def configure_logging() -> None:
    logging.basicConfig(level=os.environ.get("TOLLBRIDGE_LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s", stream=sys.stdout)


def install_signal_handlers() -> None:
    def request_stop(signum: int, frame: Any) -> None:
        LOG.info("received shutdown signal %s", signum)
        STOP.set()
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)


def run_core_bridge(pipeline: Pipeline) -> None:
    TollBridgeHandler.pipeline = pipeline
    TollBridgeHandler.quota_gate = QuotaGate(pipeline.settings.database_path)
    server = CoreBridgeServer(
        (pipeline.settings.bridge_host, pipeline.settings.bridge_port),
        TollBridgeHandler,
        pipeline.settings.max_concurrent_requests,
        pipeline.settings.request_timeout_seconds,
    )
    server.timeout = 1.0
    LOG.info("core Toll Bridge listening on %s:%d", pipeline.settings.bridge_host, pipeline.settings.bridge_port)
    try:
        while not STOP.is_set():
            server.handle_request()
    finally:
        server.server_close()


def run_worker(pipeline: Pipeline) -> None:
    consumer = f"{socket.gethostname()}-{os.getpid()}"
    LOG.info("worker started as consumer %s", consumer)
    while not STOP.is_set():
        pipeline.heartbeat(consumer, "worker")
        pipeline.process_once(consumer)


def run_mesh(pipeline: Pipeline) -> None:
    node_id = f"{socket.gethostname()}-mesh"
    LOG.info("mesh index started as %s", node_id)
    while not STOP.wait(max(1, pipeline.settings.node_ttl_seconds // 3)):
        pipeline.heartbeat(node_id, "mesh-index")


def main() -> int:
    parser = argparse.ArgumentParser(description="Tollbridge local pipeline runtime")
    parser.add_argument("role", choices=("bridge", "worker", "mesh", "health"))
    args = parser.parse_args()
    configure_logging()
    install_signal_handlers()
    settings = Settings.load()
    pipeline = Pipeline(settings)
    pipeline.initialize()
    if args.role == "bridge":
        run_core_bridge(pipeline)
    elif args.role == "worker":
        run_worker(pipeline)
    elif args.role == "mesh":
        run_mesh(pipeline)
    else:
        print(json.dumps(pipeline.health(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
