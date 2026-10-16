import unittest
from arbitrage.opportunity_detector import OpportunityDetector
from arbitrage.execution_simulator import ExecutionSimulator

class TestArbitrageDetector(unittest.TestCase):
    def test_opportunity_detection(self):
        detector = OpportunityDetector()
        tick = {
            "bid_b": 101.0, "ask_a": 100.0, 
            "depth_a": 50.0, "depth_b": 50.0, 
            "latency_ms": 5.0, "order_notional": 1000.0
        }
        res = detector.evaluate_edge(tick)
        self.assertIn("executable", res)

    def test_exposure_accumulation_and_release(self):
        sim = ExecutionSimulator(initial_capital=100000.0)
        opp = {
            "gross_spread": 0.01, "fees": 0.0005, "slippage": 0.0002, 
            "risk_cost": 0.0001, "net_edge": 0.0092, "depth_a": 15000.0, "depth_b": 15000.0
        }
        sim.simulate_order_lifecycle(opp, opp["depth_a"], opp["depth_b"])
        self.assertGreater(sim.metrics["max_exposure"], 0.0, "Max exposure must be tracked during lifecycle execution.")

if __name__ == "__main__":
    unittest.main()
