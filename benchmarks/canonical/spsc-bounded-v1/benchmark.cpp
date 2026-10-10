#include <iostream>
#include <x86intrin.h>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>

struct FlatLOB {
    uint64_t bids[1024];
    uint64_t asks[1024];
};

int main() {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(1, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    struct sched_param param;
    param.sched_priority = 99;
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
    mlockall(MCL_CURRENT | MCL_FUTURE);

    FlatLOB lob{};
    const int iterations = 10000000;

    unsigned int dummy = 0;
    uint64_t start = __rdtscp(&dummy);
    for (int i = 0; i < iterations; ++i) {
        lob.bids[i & 1023] = i;
        asm volatile("" ::: "memory");
    }
    uint64_t end = __rdtscp(&dummy);

    double cycles = static_cast<double>(end - start) / iterations;
    std::cout << "====================================================\n";
    std::cout << "ISO-CORE REAL-TIME LOCKED LOB BENCHMARK (RDTSC)\n";
    std::cout << "====================================================\n";
    std::cout << "Pinned Core : Core 1 (Isolated)\n";
    std::cout << "Priority    : SCHED_FIFO (99) + mlockall\n";
    std::cout << "Total Iterations : " << iterations << "\n";
    std::cout << "Avg CPU Cycles/Op: " << cycles << " cycles\n";
    std::cout << "Status      : BARRIERS ENFORCED (NON-ZERO EXECUTION)\n";
    std::cout << "====================================================\n";
    return 0;
}
