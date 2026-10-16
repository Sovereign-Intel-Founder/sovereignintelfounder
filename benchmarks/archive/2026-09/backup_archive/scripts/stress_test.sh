#!/bin/bash
echo "Initiating deterministic jitter and CPU contention stress test..."
stress-ng --cpu 64 --timeout 5s &
./spsc_benchmark
echo "Stress test validation complete."
