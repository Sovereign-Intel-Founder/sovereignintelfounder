#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

SEC("tracepoint/syscalls/sys_enter_sendto")
int trace_sendto(void *ctx) {
    __u64 ts = bpf_ktime_get_ns();
    bpf_printk("eBPF kernel trace: sendto triggered at timestamp %llu\n", ts);
    return 0;
}
char __license[] SEC("license") = "GPL";
