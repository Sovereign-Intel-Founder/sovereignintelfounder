CC = gcc
CFLAGS = -O3 -Wall -Wextra -pthread

all: ingestion_worker latency_worker spsc_benchmark afxdp_ingest numa_alloc simd_match consensus_node

ingestion_worker: src/ingestion_worker.c
	$(CC) $(CFLAGS) src/ingestion_worker.c -o ingestion_worker

latency_worker: src/latency_worker.c
	$(CC) $(CFLAGS) src/latency_worker.c -o latency_worker

spsc_benchmark: src/spsc_benchmark.c
	$(CC) $(CFLAGS) src/spsc_benchmark.c -o spsc_benchmark

afxdp_ingest: src/afxdp_ingest.c
	$(CC) $(CFLAGS) src/afxdp_ingest.c -o afxdp_ingest

numa_alloc: src/numa_alloc.c
	$(CC) $(CFLAGS) src/numa_alloc.c -o numa_alloc -lnuma

simd_match: simd/vector_match.c
	$(CC) -O3 -mavx512f simd/vector_match.c -o simd_match

consensus_node: consensus/raft_node.c
	$(CC) $(CFLAGS) consensus/raft_node.c -o consensus_node

clean:
	rm -f ingestion_worker latency_worker spsc_benchmark afxdp_ingest numa_alloc simd_match consensus_node ebpf/*.o /dev/shm/spsc_queue
