import time
def ramp_test(c):
    print(f"Concurrency batch: {c}")
    start = time.perf_counter_ns()
    data = [float(i) * 1.0001 for i in range(c)]
    _ = [x * 2.0 for x in data]
    print(f"Latency: {time.perf_counter_ns() - start} ns")
if __name__ == "__main__":
    for step in [1000, 10000, 100000, 1000000]:
        ramp_test(step)
        time.sleep(1)
