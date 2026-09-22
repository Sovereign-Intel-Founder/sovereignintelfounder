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

    def test_exposure_accumulation_and_release(self):
        from arbitrage.execution_simulator import ExecutionSimulator
        sim = ExecutionSimulator(initial_capital=100000.0)
        # Verify that concurrent or sequential trades appropriately track and bound exposure
        opp = {
            "gross_spread": 0.01, "fees": 0.0005, "slippage": 0.0002, 
            "risk_cost": 0.0001, "net_edge": 0.0092, "depth_a": 15000.0, "depth_b": 15000.0
        }
        sim.simulate_order_lifecycle(opp, opp["depth_a"], opp["depth_b"])
        self.assertGreater(sim.metrics["max_exposure"], 0.0, "Max exposure must be tracked during lifecycle execution.")
