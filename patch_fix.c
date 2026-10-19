// High-resolution timing fix replacement block
#include <time.h>
#include <stdio.h>

void get_high_res_time(struct timespec *start) {
    clock_gettime(CLOCK_MONOTONIC, start);
}

double elapsed_time_ms(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) * 1000.0 + (end->tv_nsec - start->tv_nsec) / 1000000.0;
}
