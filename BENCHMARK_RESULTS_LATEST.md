# SIP Core Bare-Metal Benchmark Telemetry
**Execution Time:** 2026-09-29 01:15:39 UTC
**Host Node:** s12590275 (Linux 6.1.0-53-amd64 x86_64)
**CPU Core Count:** 128

## 1. Native C Lock-Free Ring Buffer Performance
```text
Compiled executables verified. Executing make test run:
cc -O3 -Wall -Wextra -pthread -Iinclude -Isrc -o spsc_ring_test src/spsc_ring.c
./spsc_ring_test
Lock-free SPSC queue initialized with atomic head/tail (Tail: 42)
```

## 2. Depot & Arbitrage Processing Test Telemetry
```text
test_exposure_accumulation_and_release (test_arbitrage.TestArbitrageDetector.test_exposure_accumulation_and_release) ... ok
test_opportunity_detection (test_arbitrage.TestArbitrageDetector.test_opportunity_detection) ... ok
test_initial_state (test_execution.TestExecutionSimulator.test_initial_state) ... ok
test_liquidity_exhaustion (test_execution.TestExecutionSimulator.test_liquidity_exhaustion) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
test_queue_saturation_backpressure (test_backpressure_fault.TestBackpressureAndIsolation.test_queue_saturation_backpressure)
Measures producer-consumer behavior when the consumer is throttled. ... ok
test_upstream_failure_isolation (test_backpressure_fault.TestBackpressureAndIsolation.test_upstream_failure_isolation)
Verifies that an unresponsive upstream source does not lock up local workers. ... ok
test_filter_matrix (test_depot.TestSIPDepot.test_filter_matrix) ... ok
test_ring_buffer (test_depot.TestSIPDepot.test_ring_buffer) ... ok
test_malformed_input_rejection (test_flagship_pipeline.TestFlagshipPipeline.test_malformed_input_rejection) ... ok
test_queue_capacity_and_saturation (test_flagship_pipeline.TestFlagshipPipeline.test_queue_capacity_and_saturation) ... ok
test_upstream_failure_isolation (test_flagship_pipeline.TestFlagshipPipeline.test_upstream_failure_isolation) ... ok

----------------------------------------------------------------------
Ran 7 tests in 1.258s

OK

[Telemetry] Backpressure Test: Produced 50, Dropped/Shed 0

[Telemetry] Isolation Test: Upstream freeze contained without process deadlock.
```
