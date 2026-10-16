import json
from sip_depot.shared_ring import SharedMemoryRingBuffer
from sip_depot.filter_brains import BrainFilterMatrix
from sip_depot.bot_depot import CircuitBreaker, BotDepot

def run_simulation():
    ring = SharedMemoryRingBuffer(capacity=100)
    matrix = BrainFilterMatrix()
    breaker = CircuitBreaker()
    depot = BotDepot(pool_size=3)

    sample_ticks = [
        {"bid": 100.80, "ask": 100.50, "depth_a": 15.0, "depth_b": 20.0, "velocity": 120.0, "volatility": 1.1, "latency_ms": 4.2, "est_slippage": 0.002, "fees": 0.10, "node_status": "HEALTHY", "entropy": 0.4, "route_clear": True, "mempool_load": 0.3, "finality_delta_ms": 50.0},
        {"bid": 100.10, "ask": 100.05, "depth_a": 5.0, "depth_b": 2.0, "velocity": 600.0, "volatility": 3.0, "latency_ms": 25.0, "est_slippage": 0.02, "fees": 0.10, "node_status": "DEGRADED", "entropy": 0.9, "route_clear": False, "mempool_load": 0.9, "finality_delta_ms": 400.0}
    ]

    results = []
    for idx, tick in enumerate(sample_ticks):
        ring.push(tick)
        raw_tick = ring.pop()

        if not breaker.check():
            results.append({"tick": idx, "status": "CIRCUIT_BREAKER_TRIPPED"})
            continue

        passed, reason = matrix.evaluate(raw_tick)
        if passed:
            bot = depot.acquire_bot()
            if bot:
                results.append({"tick": idx, "status": "EXECUTED", "bot_id": bot["bot_id"], "reason": reason})
                depot.return_bot(bot)
            else:
                results.append({"tick": idx, "status": "DEPOT_EXHAUSTED"})
        else:
            results.append({"tick": idx, "status": "FILTERED_OUT", "reason": reason})

    with open("sip_depot/results/execution_trace.json", "w") as out:
        json.dump(results, out, indent=2)
    print("SIP Bot Depot simulation executed successfully.")

if __name__ == "__main__":
    run_simulation()
