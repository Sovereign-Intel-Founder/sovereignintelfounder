import time
import sys

def ramp_test(concurrency):
    print(f"Running iteration with concurrency batch: {concurrency}")
    start_ns = time.perf_counter_ns()
    
    # Simulate parallel tick evaluations across core batches
    data = [float(i) * 1.0001 for i in range(concurrency)]
    processed = [x * 2.0 for x in data]
    
    end_ns = time.perf_counter_ns()
    print(f"Batch latency: {end_ns - start_ns} ns")

if __name__ == "__main__":
    steps = [1000, 10000, 100000, 1000000]
    for step in steps:
        ramp_test(step)
        time.sleep(1) # Cool-down to protect server capacity
