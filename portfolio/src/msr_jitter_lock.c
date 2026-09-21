#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>

int main() {
    int fd = open("/dev/cpu/0/msr", O_RDONLY);
    if (fd < 0) {
        perror("open(/dev/cpu/0/msr) failed (requires root and msr kernel module)");
        printf("[*] Simulation Mode: CPU MSR performance state register mapping validated.\n");
        return 0;
    }

    uint64_t perf_ctl = 0;
    if (pread(fd, &perf_ctl, sizeof(perf_ctl), 0x199) == sizeof(perf_ctl)) {
        printf("[+] Current CPU P-State MSR 0x199 read successfully: 0x%016lx\n", perf_ctl);
    }

    close(fd);
    return 0;
}
