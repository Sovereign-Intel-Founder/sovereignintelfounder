import json
from arbitrage.opportunity_detector import OpportunityDetector

def run_sensitivity_analysis():
    print("[*] Running SIP Arbitrage Sensitivity Analysis...")
    
    test_ticks = [
        {"ask_a": 100.0, "bid_b": 100.8, "depth_a": 15.0, "depth_b": 20.0},
        {"ask_a": 100.0, "bid_b": 100.1, "depth_a": 5.0, "depth_b": 5.0},
        {"ask_a": 105.0, "bid_b": 106.2, "depth_a": 25.0, "depth_b": 30.0},
        {"ask_a": 98.5,  "bid_b": 99.2,  "depth_a": 12.0, "depth_b": 14.0},
    ]

    scenarios = [
        {"name": "Zero latency, zero fees", "lat": 0.0, "fees": 0.0, "slippage": 0.0},
        {"name": "Realistic fees & slippage", "lat": 0.5, "fees": 0.0005, "slippage": 0.0002},
        {"name": "1 ms latency penalty", "lat": 1.0, "fees": 0.0005, "slippage": 0.0002},
        {"name": "5 ms latency penalty", "lat": 5.0, "fees": 0.0005, "slippage": 0.0005},
        {"name": "High slippage & risk bounds", "lat": 10.0, "fees": 0.001, "slippage": 0.002}
    ]

    results = []
    for s in scenarios:
        detector = OpportunityDetector(fee_model=s["fees"], slippage_model=s["slippage"])
        opps_count = len(test_ticks)
        executable_count = 0
        cumulative_pnl = 0.0

        for tick in test_ticks:
            res = detector.evaluate_edge(tick, latency_ms=s["lat"])
            if res["executable"]:
                executable_count += 1
                cumulative_pnl += res["net_edge"]

        results.append({
            "condition": s["name"],
            "opportunities": opps_count,
            "executable": executable_count,
            "net_pnl": round(cumulative_pnl, 4)
        })

    with open("arbitrage/results/sensitivity_report.json", "w") as out:
        json.dump(results, out, indent=2)

    print("[+] Sensitivity Analysis Complete. Results saved to arbitrage/results/sensitivity_report.json")
    for r in results:
        cond = r['condition']
        exec_count = r['executable']
        total_opps = r['opportunities']
        net_pnl = r['net_pnl']
        print(f"    - {cond}: Executable={exec_count}/{total_opps}, Net PnL={net_pnl}")

if __name__ == "__main__":
    run_sensitivity_analysis()
