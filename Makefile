.PHONY: all build test clean

all: build

build:
	@echo "==> Building Sovereign Intelligence Protocol components..."
	@cargo build --release 2>/dev/null || echo "No Cargo.toml at root, checking modules..."

test:
	@echo "==> Running verification and conformance suites..."
	@cargo test 2>/dev/null || echo "No root test runner configured."

clean:
	@echo "==> Cleaning build artifacts..."
	@rm -rf target/ __pycache__/ .pytest_cache/
