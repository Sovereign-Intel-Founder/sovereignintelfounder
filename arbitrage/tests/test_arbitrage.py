import unittest
from arbitrage.opportunity_detector import OpportunityDetector

class TestArbitrageDetector(unittest.TestCase):
    def setUp(self):
        self.detector = OpportunityDetector(fee_model=0.0005, slippage_model=0.0002, max_inventory=25000.0)

    def test_profitable_edge(self):
        tick = {"ask_a": 100.0, "bid_b": 101.5, "depth_a": 15.0, "depth_b": 15.0, "timestamp_ms": 1000.0}
        res = self.detector.evaluate_edge(tick, current_time_ms=1010.0, latency_ms=1.0, order_notional=5000.0)
        self.assertTrue(res["executable"])
        self.assertGreater(res["net_edge"], 0.0)

    def test_stale_quote_rejection(self):
        tick = {"ask_a": 100.0, "bid_b": 101.5, "depth_a": 15.0, "depth_b": 15.0, "timestamp_ms": 900.0}
        res = self.detector.evaluate_edge(tick, current_time_ms=1000.0, latency_ms=1.0, order_notional=5000.0)
        self.assertFalse(res["executable"])
        self.assertEqual(res["reason"], "STALE_QUOTE")

    def test_inventory_limit_rejection(self):
        tick = {"ask_a": 100.0, "bid_b": 101.5, "depth_a": 15.0, "depth_b": 15.0, "timestamp_ms": 1000.0}
        # Exhaust inventory limit (25,000 max)
        self.detector.current_inventory = 24000.0
        res = self.detector.evaluate_edge(tick, current_time_ms=1010.0, latency_ms=1.0, order_notional=5000.0)
        self.assertFalse(res["executable"])
        self.assertEqual(res["reason"], "INVENTORY_LIMIT_EXCEEDED")

if __name__ == "__main__":
    unittest.main()
