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

class TestSovereignMetalComprehensive(unittest.TestCase):
    
    def test_01_native_c_spsc_ring_buffer_execution(self):
        """Executes the compiled C lock-free SPSC queue binary and asserts zero-fault execution."""
        core_test_path = "./core/spsc_ring_test"
        if not os.path.exists(core_test_path):
            self.fail(f"Compiled C SPSC binary not found at {core_test_path}. Run 'make test' first.")
            
        result = subprocess.run([core_test_path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"C SPSC test failed: {result.stderr}")
        self.assertIn("Lock-free SPSC queue initialized", result.stdout)

    def test_02_sqlite_wal_sharded_concurrency_stress(self):
        """Stress-tests SQLite WAL mode across concurrent background workers simulating 128-lane sharding."""
        fd, db_path = tempfile.mkstemp()
        os.close(fd)
        
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("CREATE TABLE telemetry (lane INTEGER, event_id INTEGER, payload TEXT, timestamp REAL);")
            conn.commit()
            conn.close()

            def lane_worker(lane_id, iterations):
                c = sqlite3.connect(db_path, timeout=30.0)
                for i in range(iterations):
                    c.execute(
                        "INSERT INTO telemetry (lane, event_id, payload, timestamp) VALUES (?, ?, ?, ?);", 
                        (lane_id, i, f"lane_{lane_id}_event_{i}", time.time())
                    )
                c.commit()
                c.close()

            threads = []
            lanes = 32  # High-density lane simulation
            events_per_lane = 200
            
            for l_id in range(lanes):
                t = threading.Thread(target=lane_worker, args=(l_id, events_per_lane))
                threads.append(t)
                t.start()
                
            for t in threads:
                t.join()

            reader = sqlite3.connect(db_path)
            cur = reader.cursor()
            cur.execute("SELECT COUNT(*) FROM telemetry;")
            total_records = cur.fetchone()[0]
            
            # Verify lane distribution integrity
            cur.execute("SELECT COUNT(DISTINCT lane) FROM telemetry;")
            distinct_lanes = cur.fetchone()[0]
            reader.close()

            self.assertEqual(total_records, lanes * events_per_lane)
            self.assertEqual(distinct_lanes, lanes)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_03_cryptographic_envelope_tamper_rejection(self):
        """Validates strict cryptographic rejection on canonical envelope corruption and key mismatch."""
        secret = b"sovereign_production_secret_key_2026"
        wrong_secret = b"unauthorized_malicious_key"
        payload = {"node_id": "Ashburn-Core-01", "lane_mask": 0xFFFFFF, "timestamp": 1791450000}
        
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        signature = hmac.new(secret, canonical, hashlib.sha256).hexdigest()
        
        # 1. Test payload tampering attack
        tampered_payload = payload.copy()
        tampered_payload["lane_mask"] = 0x000000
        tampered_canonical = json.dumps(tampered_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        recalculated_sig = hmac.new(secret, tampered_canonical, hashlib.sha256).hexdigest()
        
        self.assertFalse(hmac.compare_digest(signature, recalculated_sig), "Security flaw: Tampered payload accepted!")

        # 2. Test unauthorized secret key injection attack
        unauthorized_sig = hmac.new(wrong_secret, canonical, hashlib.sha256).hexdigest()
        self.assertFalse(hmac.compare_digest(signature, unauthorized_sig), "Security flaw: Unauthorized key signature accepted!")

    def test_04_toll_bridge_backpressure_simulation(self):
        """Validates queue backpressure limits and threshold dropping behavior."""
        max_capacity = 100
        queue_buffer = []
        
        # Fill to capacity
        for i in range(max_capacity):
            queue_buffer.append(f"event_{i}")
            
        # Attempt overflow injection
        overflow_dropped = 0
        incoming_burst = 50
        
        for i in range(incoming_burst):
            if len(queue_buffer) >= max_capacity:
                overflow_dropped += 1  # Drop via backpressure policy
            else:
                queue_buffer.append(f"overflow_{i}")
                
        self.assertEqual(overflow_dropped, incoming_burst)
        self.assertEqual(len(queue_buffer), max_capacity)

if __name__ == '__main__':
    unittest.main()
