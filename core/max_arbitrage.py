import time
from multiprocessing import Pool

def work_batch(c):
    data = [float(i) * 1.0001 for i in range(c)]
    _ = [x * 2.0 for x in data]

if __name__ == "__main__":
    batch_size = 10_000_000
    print(f"Launching max load test with {batch_size} iterations...")
    
    start = time.perf_counter_ns()
    with Pool(processes=32) as pool:
        pool.map(work_batch, [batch_size // 32 for _ in range(32)])
    
    print(f"Total Max Latency: {time.perf_counter_ns() - start} ns")
