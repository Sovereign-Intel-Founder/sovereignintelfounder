CC = gcc
CFLAGS = -O3 -march=native -Wall -Wextra
LIBS = -lsqlite3 -lpthread -ldl

all: toll_bridge

toll_bridge: src/toll_bridge.c
	$(CC) $(CFLAGS) src/toll_bridge.c -o toll_bridge $(LIBS)

clean:
	rm -f toll_bridge sip_ledger.db
