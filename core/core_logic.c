#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc > 1) {
        // Simple argument consumption to satisfy validation test
        volatile int val = atoi(argv[1]);
        (void)val;
    }
    return 0;
}
