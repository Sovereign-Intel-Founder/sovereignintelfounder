import glob, statistics

logs = sorted(glob.glob("/tmp/sip-resource-audit/*.log"))
results = {}

for log in logs:
    with open(log, "r") as f:
        content = f.read()
    lanes = int([l.split("Lanes=")[1].split(",")[0] for l in content.split("\n") if "Config:" in l][0])
    tp = float([l.split("Aggregate Throughput: ")[1].split(" ops/sec")[0] for l in content.split("\n") if "Aggregate Throughput:" in l][0])
    rss = int([l.split("Peak Resident Set Size (RSS): ")[1].split(" KB")[0] for l in content.split("\n") if "Peak Resident Set Size (RSS):" in l][0])
    cpu_util = float([l.split("CPU Utilization Estimate: ")[1].split("%")[0] for l in content.split("\n") if "CPU Utilization Estimate:" in l][0])
    ctxt_line = [l for l in content.split("\n") if "Context Switches" in l][0]
    nvcsw = int(ctxt_line.split("Voluntary / Involuntary): ")[1].split(" / ")[0])
    nivcsw = int(ctxt_line.split("Voluntary / Involuntary): ")[1].split(" / ")[1])
    total_ctxt = nvcsw + nivcsw
    max_q = int([l.split("MaxQSize=")[1].split(",")[0] for l in content.split("\n") if "Queue State:" in l][0])
    q_full = int([l.split("QueueFullObs=")[1].split(",")[0] for l in content.split("\n") if "Queue State:" in l][0])

    if lanes not in results:
        results[lanes] = {"tp": [], "rss": [], "cpu": [], "ctxt": [], "max_q": [], "q_full": []}
    results[lanes]["tp"].append(tp)
    results[lanes]["rss"].append(rss)
    results[lanes]["cpu"].append(cpu_util)
    results[lanes]["ctxt"].append(total_ctxt)
    results[lanes]["max_q"].append(max_q)
    results[lanes]["q_full"].append(q_full)

print("RESOURCE-INSTRUMENTED SHARDED-SPSC SCALING AUDIT")
print("=" * 95)
print(f"{'Lane Count':<12} | {'Min TP (M)':<12} | {'Med TP (M)':<12} | {'Max TP (M)':<12} | {'StdDev (M)':<12} | {'CV (%)':<8}")
print("-" * 95)
for lanes in sorted(results.keys()):
    tps = [t / 1e6 for t in results[lanes]["tp"]]
    min_tp = min(tps)
    med_tp = statistics.median(tps)
    max_tp = max(tps)
    stdev_tp = statistics.pstdev(tps) if len(tps) > 1 else 0.0
    cv_tp = (stdev_tp / med_tp) * 100 if med_tp > 0 else 0.0
    print(f"{lanes:<12} | {min_tp:<12.2f} | {med_tp:<12.2f} | {max_tp:<12.2f} | {stdev_tp:<12.2f} | {cv_tp:<8.2f}")

print("=" * 95)
print("\nResource Metrics Summary (Medians across runs):")
print(f"{'Lane Count':<12} | {'Med CPU Util (%)':<18} | {'Med RSS (KB)':<15} | {'Med Ctxt Sw':<15} | {'Med MaxQSize':<15} | {'Queue Full Obs':<15}")
print("-" * 95)
for lanes in sorted(results.keys()):
    med_cpu = statistics.median(results[lanes]["cpu"])
    med_rss = statistics.median(results[lanes]["rss"])
    med_ctxt = statistics.median(results[lanes]["ctxt"])
    med_mq = statistics.median(results[lanes]["max_q"])
    med_qf = statistics.median(results[lanes]["q_full"])
    print(f"{lanes:<12} | {med_cpu:<18.2f} | {med_rss:<15} | {med_ctxt:<15} | {med_mq:<15} | {med_qf:<15}")
