class OpportunityDetector:
    def __init__(self, fee_model=0.0005, slippage_model=0.0002):
        self.fee_rate = fee_model
        self.slippage_rate = slippage_model

    def evaluate_edge(self, tick, latency_ms=1.0):
        gross_spread = tick["bid_b"] - tick["ask_a"]
        fees = (tick["ask_a"] + tick["bid_b"]) * self.fee_rate
        slippage = (tick["ask_a"] + tick["bid_b"]) * self.slippage_rate
        network_cost = latency_ms * 0.0001
        latency_penalty = latency_ms * 0.0005
        
        net_edge = gross_spread - fees - slippage - network_cost - latency_penalty
        
        is_executable = (
            net_edge > 0 and
            tick["depth_a"] >= 10.0 and
            tick["depth_b"] >= 10.0 and
            latency_ms <= 15.0
        )
        
        return {
            "gross_spread": round(gross_spread, 4),
            "fees": round(fees, 4),
            "slippage": round(slippage, 4),
            "net_edge": round(net_edge, 4),
            "executable": is_executable
        }
