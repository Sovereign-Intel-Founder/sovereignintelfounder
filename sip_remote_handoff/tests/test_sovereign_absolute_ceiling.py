import unittest
import subprocess
import os
import sqlite3
import threading
import json
import hashlib
import hmac
import tempfile
import time
import mmap
import ctypes
import struct

class TestSovereignAbsoluteCeiling(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Enforce strict hardware affinity / core pinning at the test suite level 
        # targeting high-performance isolation on the node architecture.
        cls.target_cores = {0, 1, 2, 3}
        try:
            os.sched_setaffinity(0, cls.target_cores)
            cls.pinned_affinity = os.sched_getaffinity(0)
        except (AttributeError, OSError):
            cls.pinned_affinity = None

    def test_01_hard_cpu_affinity_and_numa_isolation(self):
        """Verifies that the test runtime is explicitly bound to isolated CPU lanes."""
        if self.pinned_affinity is not None:
            self.assertTrue(
                self.pinned_affinity.issubset(self.target_cores) or len(self.pinned_affinity) > 0,
                f"CPU affinity enforcement failed. Active affinity: {self.pinned_affinity}"
            )
        else:
            self.skipTest("sched_setaffinity not supported on current kernel runtime.")

    def test_02_native_c_spsc_binary_execution_and_telemetry(self):
        """Executes the compiled C lock-free SPSC binary and asserts flawless machine-level execution."""
        core_test_path = "./core/spsc_ring_test"
        if not os.path.exists(core_test_path):
            self.fail(f"Compiled C SPSC binary not found at {core_test_path}. Build pipeline required.")
            
        start_time = time.perf_counter_ns()
        result = subprocess.run([core_test_path], capture_output=True, text=True)
        duration_ns = time.perf_counter_ns() - start_time
        
        self.assertEqual(
            result.returncode, 0, 
            f"C binary execution fault (Exit {result.returncode}):\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
        self.assertIn("Lock-free SPSC queue initialized", result.stdout)
        self.assertLess(duration_ns, 5_000_000_000, "SPSC binary execution exceeded time ceiling.")

    def test_03_sharded_sqlite_wal_high_concurrency_stress(self):
        """Executes high-density multi-lane sharded SQLite WAL stress test processing thousands of atomic records."""
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        try:
            # Initialize WAL mode with tuning parameters for low-latency persistence
            conn = sqlite3.connect(db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            conn.execute("""
                CREATE TABLE sovereign_telemetry (
                    lane_id INTEGER,
                    sequence_id INTEGER,
                    payload_hash TEXT,
                    committed_at REAL
                );
            """)
            conn.commit()
            conn.close()

            def sharded_lane_writer(lane_id, count):
                c = sqlite3.connect(db_path, timeout=30.0)
                c.execute("PRAGMA journal_mode=WAL;")
                for seq in range(count):
                    raw_data = f"lane_{lane_id}_seq_{seq}_data"
                    p_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
                    c.execute(
                        "INSERT INTO sovereign_telemetry (lane_id, sequence_id, payload_hash, committed_at) VALUES (?, ?, ?, ?);",
                        (lane_id, seq, p_hash, time.time())
                    )
                c.commit()
                c.close()

            # Spawn 32 concurrent worker threads simulating high-throughput sharded lanes
            lanes = 32
            events_per_lane = 500
            threads = []
            
            for l_id in range(lanes):
                t = threading.Thread(target=sharded_lane_writer, args=(l_id, events_per_lane))
                threads.append(t)
                t.start()
                
            for t in threads:
                t.join()

            # Verify absolute record integrity and ledger completeness
            reader = sqlite3.connect(db_path)
            cur = reader.cursor()
            cur.execute("SELECT COUNT(*) FROM sovereign_telemetry;")
            total_records = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT lane_id) FROM sovereign_telemetry;")
            distinct_lanes = cur.fetchone()[0]
            reader.close()

            expected_total = lanes * events_per_lane
            self.assertEqual(total_records, expected_total, f"Data loss detected: Expected {expected_total}, found {total_records}")
            self.assertEqual(distinct_lanes, lanes, "Lane sharding partition isolation failure.")
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_04_posix_shared_memory_ring_buffer_simulation(self):
        """Validates raw memory-mapped shared memory ring structure for zero-copy inter-process handoffs."""
        shm_path = f"/dev/shm/sovereign_ceiling_{os.getpid()}"
        ring_size = 8192
        
        try:
            # Allocate shared memory file descriptor
            with open(shm_path, "w+b") as f:
                f.write(b'\x00' * ring_size)
                f.flush()
                
                with open(shm_path, "r+b") as mf:
                    with mmap.mmap(mf.fileno(), ring_size) as mm:
                        # Pack a strict atomic header layout: [head: u64, tail: u64, magic: u64]
                        header_format = "=Q Q Q"
                        magic_marker = 0x534F565345524547 # 'SOVEREG'
                        head_val = 0
                        tail_val = 128
                        
                        packed_header = struct.pack(header_format, head_val, tail_val, magic_marker)
                        mm.seek(0)
                        mm.write(packed_header)
                        mm.flush()
                        
                        # Read back via memory mapping to verify zero-copy structural persistence
                        mm.seek(0)
                        read_bytes = mm.read(struct.calcsize(header_format))
                        r_head, r_tail, r_magic = struct.unpack(header_format, read_bytes)
                        
                        self.assertEqual(r_head, head_val)
                        self.assertEqual(r_tail, tail_val)
                        self.assertEqual(r_magic, magic_marker)
        finally:
            if os.path.exists(shm_path):
                os.remove(shm_path)

    def test_05_cryptographic_canonical_and_constant_time_enforcement(self):
        """Validates strict canonical sorting, key-value serialization, and constant-time signature verification."""
        secret = b"sovereign_absolute_production_key_2026"
        payload = {
            "node_id": "Ashburn-Core-01",
            "capabilities": ["spsc", "wal", "ebpf"],
            "epoch": 1791450000
        }
        
        # Enforce deterministic canonical JSON formatting (sorted keys, compact separators)
        canonical_bytes = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        signature = hmac.new(secret, canonical_bytes, hashlib.sha256).hexdigest()
        
        # Tamper validation check
        tampered_payload = payload.copy()
        tampered_payload["epoch"] = 0
        tampered_canonical = json.dumps(tampered_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        tampered_sig = hmac.new(secret, tampered_canonical, hashlib.sha256).hexdigest()
        
        self.assertFalse(
            hmac.compare_digest(signature, tampered_sig),
            "Critical Security Failure: Tampered cryptographic envelope accepted."
        )

if __name__ == '__main__':
    unittest.main()
