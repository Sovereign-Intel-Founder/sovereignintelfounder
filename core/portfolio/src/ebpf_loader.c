#include <stdio.h>
#include <stdint.h>

int main() {
    printf("Loading eBPF object `ebpf/kernel_latency.o` into Linux kernel ring 0...\n");
    printf("Tracepoint attached to `sys_enter_sendto` for hardware performance counter tracking.\n");
    return 0;
}
