class BrainFilterMatrix:
    def __init__(self):
        self.brains = [self._brain_spread, self._brain_depth, self._brain_velocity,
                       self._brain_volatility, self._brain_latency, self._brain_slippage,
                       self._brain_fee_margin, self._brain_node_health, self._brain_entropy,
                       self._brain_routing, self._brain_congestion, self._brain_finality]

    def evaluate(self, tick):
        for i, brain in enumerate(self.brains):
            passed, reason = brain(tick)
            if not passed:
                return False, f"Brain {i+1} Rejected: {reason}"
        return True, "All 12 Brains Approved"

    def _brain_spread(self, t): return (t["bid"] - t["ask"]) > 0.05, "Spread too narrow"
    def _brain_depth(self, t): return t["depth_a"] > 10.0 and t["depth_b"] > 10.0, "Insufficient depth"
    def _brain_velocity(self, t): return t["velocity"] < 500.0, "Tick velocity anomaly"
    def _brain_volatility(self, t): return t["volatility"] < 2.5, "Excessive volatility"
    def _brain_latency(self, t): return t["latency_ms"] < 15.0, "Propagation latency high"
    def _brain_slippage(self, t): return t["est_slippage"] < 0.01, "Slippage tolerance exceeded"
    def _brain_fee_margin(self, t): return (t["bid"] - t["ask"]) > t["fees"], "Fee erosion risk"
    def _brain_node_health(self, t): return t["node_status"] == "HEALTHY", "Node degraded"
    def _brain_entropy(self, t): return t["entropy"] < 0.8, "Market entropy spike"
    def _brain_routing(self, t): return t["route_clear"] is True, "Route blocked"
    def _brain_congestion(self, t): return t["mempool_load"] < 0.7, "Network congestion"
    def _brain_finality(self, t): return t["finality_delta_ms"] < 200.0, "Finality lag"
