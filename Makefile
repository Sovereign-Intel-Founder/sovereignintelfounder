CC = gcc
CFLAGS = -O3 -march=native -mavx512f -mavx512cd -std=gnu11 -pthread
INCLUDES = -I 02-low-latency/bitstream/include \
           -I 02-low-latency/bitstream/tests \
           -I 02-low-latency/toll_bridge/include \
           -I 02-low-latency/mesh_index/include
LIBS = -lnuma

all: sovereign_live_engine

sovereign_live_engine:
	$(CC) $(CFLAGS) \
		02-low-latency/bitstream/tests/test_live_engine.c \
		02-low-latency/toll_bridge/src/sovereign_toll_bridge.c \
		02-low-latency/mesh_index/src/sovereign_mesh_index.c \
		$(INCLUDES) $(LIBS) -o sovereign_live_engine

clean:
	rm -f sovereign_live_engine *.log
