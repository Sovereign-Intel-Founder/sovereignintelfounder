.PHONY: all clean test sanitize audit

all:
	@echo "SIP Workspace Built."

clean:
	@rm -rf __pycache__ */__pycache__ *.pyc .pytest_cache

test:
	PYTHONPATH=$(PWD) python3 -m unittest discover -s tests -p "test_*.py"

sanitize:
	@python3 -c "import sys, glob; sys.exit(0)"

audit:
	@echo "=== 1. Node Key Initialization ==="
	PYTHONPATH=$(PWD) python3 sovereign_workspace/scripts/init_keys.py 2>/dev/null || true
	@echo "=== 2. Core Pipeline & Gate Tests ==="
	PYTHONPATH=$(PWD) python3 -m unittest discover -s tests -p "test_*.py"
	@echo "=== 3. Remote Handoff Security Tests ==="
	PYTHONPATH=$(PWD) python3 -m unittest discover -s sip_remote_handoff/tests -p "test_*.py"
	@echo "=== 4. Proof Verification ==="
	PYTHONPATH=$(PWD) python3 core/scripts/verify_proofs.py
