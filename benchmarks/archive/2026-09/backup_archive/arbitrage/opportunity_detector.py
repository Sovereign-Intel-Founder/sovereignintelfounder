class OpportunityDetector:
    def __init__(self, fee_model=0.0005, slippage_model=0.0002, max_inventory=50000.0):
        self.fee_rate = fee_model
        self.slippage_rate = slippage_model
        self.max_inventory = max_inventory
        self.current_inventory = 0.0

    def evaluate_edge(self, tick, current_time_ms=1000.0, latency_ms=1.0, order_notional=10000.0):
        tick_time = tick.get("timestamp_ms", 1000.0)
        if (current_time_ms - tick_time) > 50.0:
            return {"executable": False, "reason": "STALE_QUOTE", "net_edge": 0.0}

        if (self.current_inventory + order_notional) > self.max_inventory:
            return {"executable": False, "reason": "INVENTORY_LIMIT_EXCEEDED", "net_edge": 0.0}

        gross_spread = tick["bid_b"] - tick["ask_a"]
        fees = (tick["ask_a"] + tick["bid_b"]) * self.fee_rate
        slippage = (tick["ask_a"] + tick["bid_b"]) * self.slippage_rate
        network_cost = latency_ms * 0.0001
        latency_penalty = latency_ms * 0.0005
        risk_cost = (order_notional / self.max_inventory) * 0.001
        
        net_edge = gross_spread - fees - slippage - network_cost - latency_penalty - risk_cost
        
        is_executable = (
            net_edge > 0 and
            tick["depth_a"] >= 10.0 and
            tick["depth_b"] >= 10.0 and
            latency_ms <= 15.0
        )
        
        if is_executable:
            self.current_inventory += order_notional

        return {
            "gross_spread": round(gross_spread, 4),
            "fees": round(fees, 4),
            "slippage": round(slippage, 4),
            "risk_cost": round(risk_cost, 4),
            "net_edge": round(net_edge, 4),
            "executable": is_executable,
            "reason": "EXECUTABLE" if is_executable else "NEGATIVE_EDGE_OR_DEPTH"
        }
