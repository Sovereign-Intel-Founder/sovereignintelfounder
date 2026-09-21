import time
import json
import multiprocessing as mp
from arbitrage.execution_simulator import ExecutionSimulator
import random

def worker_batch(batch_id, num_ticks):
    sim = ExecutionSimulator(initial_capital=100000.0)
    random.seed(42 + batch_id)
    stream = [
        {"gross_spread": 0.008, "fees": 0.0005, "slippage": 0.0002, "risk_cost": 0.0001, "net_edge": 0.0072, "depth_a": 12000.0, "depth_b": 15000.0},
        {"gross_spread": 0.012, "fees": 0.0005, "slippage": 0.0004, "risk_cost": 0.0002, "net_edge": 0.0109, "depth_a": 4000.0, "depth_b": 12000.0},
        {"gross_spread": 0.005, "fees": 0.0005, "slippage": 0.0001, "risk_cost": 0.0001, "net_edge": 0.0043, "depth_a": 20000.0, "depth_b": 25000.0},
        {"gross_spread": 0.009, "fees": 0.0005, "slippage": 0.0002, "risk_cost": 0.0001, "net_edge": 0.0082, "depth_a": 18000.0, "depth_b": 19000.0},
    ] * (num_ticks // 4)
    for opp in stream:
        sim.simulate_order_lifecycle(opp, opp["depth_a"], opp["depth_b"])
    return sim.metrics

def run_mass_scale_simulation():
    total_target_ticks = 5000000
    num_workers = min(mp.cpu_count(), 16)
    ticks_per_worker = total_target_ticks // num_workers
    
    start_time = time.perf_counter()
    with mp.Pool(num_workers) as pool:
        reports = pool.starmap(worker_batch, [(i, ticks_per_worker) for i in range(num_workers)])
    duration = time.perf_counter() - start_time
    
    agg = {
        "simulation_classification": "Seeded synthetic execution-lifecycle simulation",
        "workload_events": total_target_ticks,
        "worker_count": num_workers,
        "seed": 42,
        "measurement_boundary": "Multiprocess worker batch aggregate wall-clock time",
        "hardware_context": "Local multi-core host",
        "duration_seconds": round(duration, 4),
        "throughput_events_per_sec": round(total_target_ticks / duration, 2),
        "metrics": {
            "total_opportunities": sum(w["total_opportunities"] for w in reports),
            "executed_trades": sum(w["executed_trades"] for w in reports),
            "profitable_trades": sum(w["profitable_trades"] for w in reports),
            "losing_trades": sum(w["losing_trades"] for w in reports),
            "breakeven_trades": sum(w["breakeven_trades"] for w in reports),
            "partial_fills": sum(w["partial_fills"] for w in reports),
            "failed_legs": sum(w["failed_legs"] for w in reports),
            "expired_quotes": sum(w["expired_quotes"] for w in reports),
            "gross_pnl": round(sum(w["gross_pnl"] for w in reports), 2),
            "total_fees": round(sum(w["total_fees"] for w in reports), 2),
            "total_slippage": round(sum(w["total_slippage"] for w in reports), 2),
            "net_pnl": round(sum(w["net_pnl"] for w in reports), 2),
            "max_exposure": round(max(w["max_exposure"] for w in reports), 2),
        }
    }
    
    with open("arbitrage/results/mass_scale_report.json", "w") as out:
        json.dump(agg, out, indent=2)
    print(f"[+] Complete. Throughput: {agg['throughput_events_per_sec']:,} events/sec")

if __name__ == "__main__":
    run_mass_scale_simulation()
