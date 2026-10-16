.PHONY: init-db run-settlement run-node mesh-up clean-wal test-mesh

init-db:
	python3 -c "import sqlite3; conn = sqlite3.connect('sovereign_intel.db'); conn.execute('PRAGMA journal_mode=WAL;'); conn.commit(); conn.close()"
	@echo "[MAKE] SQLite WAL ledger initialized."

run-settlement: init-db
	python3 services/settlement_listener.py

run-node: init-db
	PYTHONPATH=. python3 core/engine.py

mesh-up: init-db
	@echo "[MAKE] Spinning up local mesh node services..."
	python3 services/settlement_listener.py &
	PYTHONPATH=. python3 core/engine.py

clean-wal:
	rm -f sovereign_intel.db sovereign_intel.db-shm sovereign_intel.db-wal
	@echo "[MAKE] Purged compiled binaries, object files, and WAL journals."

test-mesh:
	PYTHONPATH=../.. python3 ../../scripts/test_node_config.py
