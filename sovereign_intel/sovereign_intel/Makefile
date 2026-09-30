CC = gcc
CFLAGS = -O3 -march=native -Wall -Wextra -pthread -Isovereign_intel/core
SQLITE_FLAGS = -O3 -march=native -w -pthread -Isovereign_intel/core

TARGET = sip_engine
SRC_ENGINE = sovereign_intel/core/sip_persistence.c
SRC_SQLITE = sovereign_intel/core/sqlite3.c
PYTHON = python3

.PHONY: all clean test run-engine verify-db

all: $(TARGET)

sqlite3.o: $(SRC_SQLITE)
	@echo "[BUILD] Compiling SQLite amalgamation (suppressing external warnings)..."
	$(CC) $(SQLITE_FLAGS) -c $(SRC_SQLITE) -o sqlite3.o

sip_persistence.o: $(SRC_ENGINE)
	@echo "[BUILD] Compiling Sovereign Intelligence engine..."
	$(CC) $(CFLAGS) -c $(SRC_ENGINE) -o sip_persistence.o

$(TARGET): sip_persistence.o sqlite3.o
	@echo "[LINK] Linking binary executable $(TARGET)..."
	$(CC) sip_persistence.o sqlite3.o -ldl -lpthread -o $(TARGET)
	@echo "[SUCCESS] Build complete: ./$(TARGET)"

run-engine: $(TARGET)
	@echo "[EXEC] Running bare-metal C ingestion and persistence engine..."
	./$(TARGET)

verify-db:
	@echo "[TEST] Initializing and verifying Python SQLite WAL storage..."
	$(PYTHON) storage/db.py
	$(PYTHON) -c 'from core.engine import IntelligenceObject; print("[SUCCESS] Test lineage committed:", IntelligenceObject(claim="Makefile verification pass.", sources=["https://sip.internal/makefile"], confidence=0.999).commit())'

test: all verify-db run-engine
	@echo "[ALL SYSTEMS GO] Sovereign Intelligence Protocol pipeline verified successfully."

clean:
	@echo "[CLEAN] Purging compiled binaries, object files, and WAL journals..."
	rm -f $(TARGET) *.o sovereign_intel.db sovereign_intel.db-shm sovereign_intel.db-wal
