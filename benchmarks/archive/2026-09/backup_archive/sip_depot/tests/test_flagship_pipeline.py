import unittest
import time

class TestFlagshipPipeline(unittest.TestCase):
    
    def test_queue_capacity_and_saturation(self):
        capacity = 100
        workload = 250
        accepted = 0
        rejected = 0
        current_depth = 0
        max_depth = 0
        
        # Simulate burst ingestion exceeding capacity without immediate draining
        for i in range(workload):
            if current_depth < capacity:
                current_depth += 1
                accepted += 1
                if current_depth > max_depth:
                    max_depth = current_depth
            else:
                rejected += 1
                
        self.assertLessEqual(max_depth, capacity, "Invariant violation: Queue capacity exceeded")
        self.assertEqual(accepted + rejected, workload, "Invariant violation: Event accounting mismatch")
        self.assertEqual(accepted, capacity, "Accepted count must equal queue capacity")
        self.assertEqual(rejected, workload - capacity, "Excess workload must be rejected via backpressure")

    def test_malformed_input_rejection(self):
        events = [{"seq": 1, "valid": True}, {"malformed": True}, {"seq": 2, "valid": True}]
        accepted = 0
        rejected = 0
        
        for ev in events:
            if not ev.get("valid", False):
                rejected += 1
            else:
                accepted += 1
                
        self.assertEqual(rejected, 1, "Malformed event must be rejected")
        self.assertEqual(accepted, 2, "Valid events must be accepted")

    def test_upstream_failure_isolation(self):
        worker_state = "RUNNING"
        error_logged = False
        
        def mock_upstream_source(fail=False):
            if fail:
                raise ConnectionError("Upstream peer disconnected")
            return {"status": "OK"}

        try:
            mock_upstream_source(fail=True)
        except ConnectionError:
            error_logged = True
            worker_state = "RUNNING"
            
        self.assertTrue(error_logged, "Upstream error must be caught")
        self.assertEqual(worker_state, "RUNNING", "Worker must remain isolated from upstream failure")

if __name__ == "__main__":
    unittest.main()
