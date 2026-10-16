import unittest
from sip_depot.shared_ring import SharedMemoryRingBuffer
from sip_depot.filter_brains import BrainFilterMatrix
from sip_depot.bot_depot import CircuitBreaker, BotDepot

class TestSIPDepot(unittest.TestCase):
    def test_ring_buffer(self):
        ring = SharedMemoryRingBuffer(capacity=3)
        self.assertTrue(ring.push("data1"))
        self.assertEqual(ring.pop(), "data1")

    def test_filter_matrix(self):
        matrix = BrainFilterMatrix()
        good_tick = {"bid": 101.0, "ask": 100.0, "depth_a": 15.0, "depth_b": 20.0, "velocity": 100.0, "volatility": 1.0, "latency_ms": 5.0, "est_slippage": 0.001, "fees": 0.05, "node_status": "HEALTHY", "entropy": 0.5, "route_clear": True, "mempool_load": 0.2, "finality_delta_ms": 100.0}
        passed, _ = matrix.evaluate(good_tick)
        self.assertTrue(passed)

if __name__ == "__main__":
    unittest.main()
