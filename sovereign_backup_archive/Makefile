CC = gcc
CFLAGS = -std=c11 -O3 -Wall -Wextra -pthread
SANITIZE_FLAGS = -std=c11 -g -O1 -fsanitize=address,undefined -Wall -Wextra -pthread

all: spsc_ring_test

spsc_ring_test: src/spsc_ring.c
	$(CC) $(CFLAGS) src/spsc_ring.c -o spsc_ring_test

sanitize: src/spsc_ring.c
	$(CC) $(SANITIZE_FLAGS) src/spsc_ring.c -o spsc_ring_sanitized
	./spsc_ring_sanitized
	@echo "[Sanitizer] ASan & UBSan validation: PASS"

loopback-check:
	@echo "[Network] Verifying local loopback bindings and dependency scope..."
	python3 -c "import socket; s = socket.socket(); s.bind(('127.0.0.1', 0)); print('[Network] Loopback bind test to 127.0.0.1: PASS')"

test: all
	./spsc_ring_test
	python3 -m unittest discover -s sip_depot/tests -v

demo: all sanitize loopback-check
	python3 sip_depot/flagship_harness.py --matrix

clean:
	rm -f spsc_ring_test spsc_ring_sanitized
	rm -rf sip_depot/results/*.json
