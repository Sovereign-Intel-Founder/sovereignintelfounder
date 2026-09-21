import unittest
from arbitrage.execution_simulator import ExecutionSimulator

TestExecutionSimulator = type('TestExecutionSimulator', (unittest.TestCase,), {
    'test_initial_state': lambda self: self.assertEqual(ExecutionSimulator(10000.0).capital, 10000.0),
    'test_liquidity_exhaustion': lambda self: self.assertEqual(
        ExecutionSimulator(10000.0).simulate_order_lifecycle({"gross_spread": 0.01}, 1000.0, 10000.0), 
        "EXPIRED_LIQUIDITY_GAP"
    )
})

if __name__ == "__main__":
    unittest.main()
