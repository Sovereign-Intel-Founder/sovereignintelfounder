#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint64_t term;
    uint64_t index;
    int leader_id;
} RaftLogEntry;

int main() {
    RaftLogEntry entry = {.term = 1, .index = 1042, .leader_id = 3};
    printf("Raft consensus state initialized: Term %lu, Index %lu, Leader %d\n", entry.term, entry.index, entry.leader_id);
    return 0;
}
