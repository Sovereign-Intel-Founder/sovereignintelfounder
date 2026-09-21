# Sovereign Intelligence Protocol — Root Makefile

CC = gcc
CFLAGS = -O3 -Wall -Wextra -pthread -std=c11

all: lockfree_spsc_ring

lockfree_spsc_ring: portfolio/src/lockfree_spsc_ring.c
	$(CC) $(CFLAGS) portfolio/src/lockfree_spsc_ring.c -o lockfree_spsc_ring

clean:
	rm -f lockfree_spsc_ring
