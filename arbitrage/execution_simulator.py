import json
import random

class ExecutionSimulator:
    def __init__(self, initial_capital=100000.0):
        self.capital = initial_capital
        self.max_capital = initial_capital
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0
        self.metrics = {
            "total_opportunities": 0,
            "executed_trades": 0,
            "partial_fills": 0,
            "failed_legs": 0,
            "expired_quotes": 0,
            "gross_pnl": 0.0,
            "total_fees": 0.0,
            "total_slippage": 0.0,
            "net_pnl": 0.0,
            "max_exposure": 0.0
        }

    def simulate_order_lifecycle(self, opportunity, market_depth_a, market_depth_b):
        self.metrics["total_opportunities"] += 1
        
        # Simulate execution friction & state transitions
        fill_roll = random.random()
        
        # Check L2 depth exhaustion
        required_size = 5000.0 # Notional per leg
        if market_depth_a < required_size or market_depth_b < required_size:
            self.metrics["expired_quotes"] += 1
            return "EXPIRED_LIQUIDITY_GAP"

        if fill_roll < 0.05:
            # Asymmetric Leg Failure (Risk of unhedged inventory)
            self.metrics["failed_legs"] += 1
            loss = -150.0 # Unhedged slippage penalty
            self.net_pnl_accounting(0.0, 0.0, 0.0, loss)
            return "LEG_FAILURE_EXPOSED"
        elif fill_roll < 0.20:
            # Partial Fill
            self.metrics["partial_fills"] += 1
            self.metrics["executed_trades"] += 1
            gross = opportunity["gross_spread"] * 2500.0
            fees = opportunity["fees"] * 0.5
            slip = opportunity["slippage"] * 1.5 # Higher slippage on partials
            net = gross - fees - slip - opportunity["risk_cost"]
            self.net_pnl_accounting(gross, fees, slip, net)
            return "PARTIAL_FILL"
        else:
            # Clean Full Fill
            self.metrics["executed_trades"] += 1
            gross = opportunity["gross_spread"] * 5000.0
            fees = opportunity["fees"]
            slip = opportunity["slippage"]
            net = opportunity["net_edge"] * 5000.0
            self.net_pnl_accounting(gross, fees, slip, net)
            return "FULL_FILL"

    def net_pnl_accounting(self, gross, fees, slip, net):
        self.metrics["gross_pnl"] += gross
        self.metrics["total_fees"] += fees
        self.metrics["total_slippage"] += slip
        self.metrics["net_pnl"] += net
        
        self.capital += net
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        
        drawdown = self.peak_capital - self.capital
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

def run_stress_simulation():
    print("[*] Running Advanced Arbitrage Execution & Fuzzing Simulation...")
    sim = ExecutionSimulator()
    
    # Mock stream of detected opportunities with L2 depth
    stream = [
        {"gross_spread": 0.008, "fees": 0.0005, "slippage": 0.0002, "risk_cost": 0.0001, "net_edge": 0.0072, "depth_a": 12000.0, "depth_b": 15000.0},
        {"gross_spread": 0.012, "fees": 0.0005, "slippage": 0.0004, "risk_cost": 0.0002, "net_edge": 0.0109, "depth_a": 4000.0, "depth_b": 12000.0}, # Depth gap
        {"gross_spread": 0.005, "fees": 0.0005, "slippage": 0.0001, "risk_cost": 0.0001, "net_edge": 0.0043, "depth_a": 20000.0, "depth_b": 25000.0},
        {"gross_spread": 0.009, "fees": 0.0005, "slippage": 0.0002, "risk_cost": 0.0001, "net_edge": 0.0082, "depth_a": 18000.0, "depth_b": 19000.0},
    ] * 250 # 1,000 tick stress test

    random.seed(42) # Deterministic fuzzing seed
    for opp in stream:
        sim.simulate_order_lifecycle(opp, opp["depth_a"], opp["depth_b"])

    report = {
        "simulation_ticks": len(stream),
        "metrics": {k: round(v, 4) if isinstance(v, float) else v for k, v in sim.metrics.items()},
        "final_capital": round(sim.capital, 2),
        "max_drawdown": round(sim.max_drawdown, 2),
        "win_rate_pct": round((sim.metrics["executed_trades"] - sim.metrics["failed_legs"]) / max(1, sim.metrics["executed_trades"]) * 100, 2)
    }

    with open("arbitrage/results/execution_stress_report.json", "w") as out:
        json.dump(report, out, indent=2)

    print("[+] Execution Stress Simulation Complete.")
    print(f"    - Total Opportunities: {report['simulation_ticks']}")
    print(f"    - Executed Trades: {report['metrics']['executed_trades']}")
    print(f"    - Failed Legs (Exposed): {report['metrics']['failed_legs']}")
    print(f"    - Net PnL: ${report['metrics']['net_pnl']}")
    print(f"    - Max Drawdown: ${report['max_drawdown']}")

if __name__ == "__main__":
    run_stress_simulation()
