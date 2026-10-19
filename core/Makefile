CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra -pthread -Iinclude -Isrc
SANITIZER_FLAGS ?= -fsanitize=address,undefined -g -O1 -Wall -Wextra -pthread -Iinclude -Isrc

.PHONY: all test sanitize spsc_ring_test lockfree_spsc_ring clean

all: spsc_ring_test lockfree_spsc_ring

spsc_ring_test: src/spsc_ring.c
	$(CC) $(CFLAGS) -o $@ $<

lockfree_spsc_ring: spsc_ring_test

sanitize: src/spsc_ring.c
	$(CC) $(SANITIZER_FLAGS) -o spsc_ring_test_sanitize $<
	./spsc_ring_test_sanitize

test: spsc_ring_test
	./spsc_ring_test

clean:
	rm -f spsc_ring_test spsc_ring_test_sanitize core/spsc_ring_test
