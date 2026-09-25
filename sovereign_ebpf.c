#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_XSKMAP);
    __uint(max_entries, 64);
    __type(key, int);
    __type(value, int);
} xsks_map SEC(".maps");

SEC("xdp")
int sovereign_xdp_prog(struct xdp_md *ctx)
{
    int index = ctx->rx_queue_index;
    
    /* Redirect traffic to the AF_XDP socket if bound to this queue */
    if (bpf_map_lookup_elem(&xsks_map, &index))
        return bpf_redirect_map(&xsks_map, index, 0);
        
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
