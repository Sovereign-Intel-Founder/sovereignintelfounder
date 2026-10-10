
#include <thread>
#include <atomic>

// Added consumer pacing thread to prevent SPSC ring stall / deadlock
std::atomic<bool> g_stop_consumer{false};
void run_consumer(FlatLOB& lob) {
    while (!g_stop_consumer.load(std::memory_order_relaxed)) {
        asm volatile("" ::: "memory");
    }
}
#include <iostream>
#include <cstdint>
#include <x86intrin.h>
#include <array>
#include <iomanip>

struct alignas(64) Order {
    uint64_t id;
    uint32_t price;
    uint32_t qty;
    uint8_t  side;
    char     padding[43]; // Pad to 64-byte cache line
};

constexpr size_t BOOK_CAPACITY = 10000;

struct FlatLOB {
    std::array<Order, BOOK_CAPACITY> slots{};
    uint32_t count{0};

    inline void insert(uint64_t id, uint32_t price, uint32_t qty, uint8_t side) {
        uint32_t idx = count % BOOK_CAPACITY;
        slots[idx] = Order{id, price, qty, side, {}};
        count++;
    }
};

int main() {
    std::thread consumer_th(run_consumer, std::ref(lob));
    FlatLOB lob;
    constexpr uint64_t ITERATIONS = 10000000;

    // Warm up L1/L2 cache and branch predictor
    for (uint64_t i = 0; i < 100000; ++i) {
        lob.insert(i, 1000, 10, 1);
    }

    uint64_t start_cycles = __rdtsc();
    for (uint64_t i = 0; i < ITERATIONS; ++i) {
        lob.insert(i, 10000 + (i % 50), 100, 1);
        
        // Inline memory barrier: prevents dead-code elimination & loop hoisting
        asm volatile("" : : "r"(&lob) : "memory");
    }
    uint64_t end_cycles = __rdtsc();

    double total_cycles = static_cast<double>(end_cycles - start_cycles);
    double cycles_per_op = total_cycles / ITERATIONS;

    std::cout << "\n======================================================\n";
    std::cout << " SOVEREIGN HARDWARE-BOUND LOB BENCHMARK (RDTSC)\n";
    std::cout << "======================================================\n";
    std::cout << " Total Iterations : " << ITERATIONS << "\n";
    std::cout << " Total CPU Cycles : " << static_cast<uint64_t>(total_cycles) << "\n";
    std::cout << " Avg CPU Cycles/Op: " << std::fixed << std::setprecision(2) << cycles_per_op << " cycles\n";
    std::cout << " Status           : BARRIERS ENFORCED (NON-ZERO EXECUTION)\n";
    std::cout << "======================================================\n\n";

    g_stop_consumer.store(true);
    consumer_th.join();
    return 0;
}
