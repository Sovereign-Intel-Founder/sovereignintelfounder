import json
import random

class ExecutionSimulator:
    def __init__(self, initial_capital=100000.0):
        self.capital = initial_capital
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0
        self.current_exposure = 0.0
        self.metrics = {
            "simulation_classification": "Seeded synthetic execution-lifecycle simulation",
            "total_opportunities": 0,
            "executed_trades": 0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "breakeven_trades": 0,
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
        base_notional = 5000.0
        
        if market_depth_a < base_notional or market_depth_b < base_notional:
            self.metrics["expired_quotes"] += 1
            return "EXPIRED_LIQUIDITY_GAP"

        fill_roll = random.random()
        self.current_exposure = base_notional
        if self.current_exposure > self.metrics["max_exposure"]:
            self.metrics["max_exposure"] = self.current_exposure

        try:
            if fill_roll < 0.05:
                self.metrics["failed_legs"] += 1
                self.metrics["losing_trades"] += 1
                loss = -150.0 
                self.net_pnl_accounting(0.0, 0.0, 0.0, loss)
                return "LEG_FAILURE_EXPOSED"
            elif fill_roll < 0.20:
                self.metrics["partial_fills"] += 1
                self.metrics["executed_trades"] += 1
                traded_notional = base_notional * 0.5
                gross = opportunity["gross_spread"] * traded_notional
                fees = opportunity["fees"] * traded_notional
                slippage = (opportunity["slippage"] * 1.5) * traded_notional
                risk_cost = opportunity["risk_cost"] * traded_notional
                net = gross - fees - slippage - risk_cost - 0.0001 * traded_notional
                self.net_pnl_accounting(gross, fees, slippage, net)
                self.record_trade_outcome(net)
                return "PARTIAL_FILL"
            else:
                self.metrics["executed_trades"] += 1
                traded_notional = base_notional
                gross = opportunity["gross_spread"] * traded_notional
                fees = opportunity["fees"] * traded_notional
                slippage = opportunity["slippage"] * traded_notional
                risk_cost = opportunity["risk_cost"] * traded_notional
                net = gross - fees - slippage - risk_cost - 0.0001 * traded_notional
                self.net_pnl_accounting(gross, fees, slippage, net)
                self.record_trade_outcome(net)
                return "FULL_FILL"
        finally:
            self.current_exposure = 0.0

    def record_trade_outcome(self, net_pnl):
        if net_pnl > 1e-4:
            self.metrics["profitable_trades"] += 1
        elif net_pnl < -1e-4:
            self.metrics["losing_trades"] += 1
        else:
            self.metrics["breakeven_trades"] += 1

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
