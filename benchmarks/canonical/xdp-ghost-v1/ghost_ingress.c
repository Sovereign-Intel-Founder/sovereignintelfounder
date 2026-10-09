
typedef unsigned int __u32;
typedef unsigned short __u16;
typedef unsigned char __u8;

struct xdp_md {
    __u32 data;
    __u32 data_end;
    __u32 data_meta;
    __u32 ingress_ifindex;
    __u32 rx_queue_index;
};

#define XDP_PASS 2

__attribute__((section("xdp")))
int ghost_ingress_main(struct xdp_md *ctx) {
    return XDP_PASS;
}

char _license[] __attribute__((section("license"))) = "GPL";
