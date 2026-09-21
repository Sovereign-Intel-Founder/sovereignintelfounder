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
        
    return {
        "executed": sim.metrics["executed_trades"],
        "failed": sim.metrics["failed_legs"],
        "net_pnl": sim.metrics["net_pnl"],
        "expired": sim.metrics["expired_quotes"]
    }

def run_mass_scale_simulation():
    total_target_ticks = 5000000
    num_workers = min(mp.cpu_count(), 16)
    ticks_per_worker = total_target_ticks // num_workers
    
    print(f"[*] Launching Massive-Scale Microstructure Stress Test...")
    print(f"    - Target Events: {total_target_ticks:,}")
    print(f"    - Parallel Workers: {num_workers}")
    print(f"    - Events Per Worker: {ticks_per_worker:,}")
    
    start_time = time.perf_counter()
    
    with mp.Pool(num_workers) as pool:
        results = pool.starmap(worker_batch, [(i, ticks_per_worker) for i in range(num_workers)])
        
    duration = time.perf_counter() - start_time
    
    aggregated = {
        "total_events": total_target_ticks,
        "duration_seconds": round(duration, 4),
        "throughput_events_per_sec": round(total_target_ticks / duration, 2),
        "worker_results": results
    }
    
    with open("arbitrage/results/mass_scale_report.json", "w") as out:
        json.dump(aggregated, out, indent=2)
        
    print(f"[+] Mass Scale Stress Simulation Complete.")
    print(f"    - Execution Time: {duration:.4f} seconds")
    print(f"    - Sustained Throughput: {aggregated['throughput_events_per_sec']:,} events/sec")

if __name__ == "__main__":
    run_mass_scale_simulation()
