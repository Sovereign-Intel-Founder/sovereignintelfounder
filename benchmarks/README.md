# Sovereign Intelligence Protocol — Benchmarks & Evidence

Structured repository containing canonical performance metrics, experimental primitives, and historical audit logs.

## Adding a New Benchmark

1. Run generator:
   `python3 benchmarks/tools/new_benchmark.py --id <id> --category canonical --description "<desc>"`
2. Implement code in assigned directory.
3. Update `benchmarks/MANIFEST.yaml`.
4. Run validation:
   `python3 benchmarks/tools/validate_results.py`
