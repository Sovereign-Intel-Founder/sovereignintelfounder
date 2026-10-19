.PHONY: all test benchmark clean health

all:
	@echo "=== Building & Verifying SIP Cluster =="
	python3 -c "import json; print('[+] Manifest valid:', json.load(open('system_manifest.json'))['status'])"

test:
	@echo "=== Running Test Suites =="
	python3 -m unittest discover -s tests -p "*.py"

benchmark:
	@echo "=== Executing Benchmark Workloads =="
	python3 benchmarks/comprehensive_benchmark.py

health:
	@echo "=== Running Cluster Health Audit =="
	python3 tools/cluster_health.py

clean:
	@echo "=== Cleaning temporary artifacts =="
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
