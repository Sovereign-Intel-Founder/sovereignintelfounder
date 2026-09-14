CC = gcc
CFLAGS = -O3 -Wall -Wextra -pthread

all: ingestion_worker latency_worker spsc_benchmark

ingestion_worker: ingestion_worker.c
	$(CC) $(CFLAGS) ingestion_worker.c -o ingestion_worker

latency_worker: latency_worker.c
	$(CC) $(CFLAGS) latency_worker.c -o latency_worker

spsc_benchmark: spsc_benchmark.c
	$(CC) $(CFLAGS) spsc_benchmark.c -o spsc_benchmark

clean:
	rm -f ingestion_worker latency_worker spsc_benchmark /dev/shm/spsc_queue
