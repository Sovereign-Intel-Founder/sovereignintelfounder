CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra -pthread -Iinclude -Isrc

.PHONY: all spsc_ring_test lockfree_spsc_ring

all: spsc_ring_test

lockfree_spsc_ring: spsc_ring_test

spsc_ring_test: src/spsc_ring.c
	$(CC) $(CFLAGS) -o $@ $<
