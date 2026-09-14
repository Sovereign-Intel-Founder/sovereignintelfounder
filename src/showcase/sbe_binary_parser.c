#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>

// Simple Binary Encoding (SBE) Market Data Message Schema
typedef struct {
    uint16_t block_length;
    uint16_t template_id;
    uint16_t schema_id;
    uint16_t version;
} __attribute__((packed)) sbe_header_t;

typedef struct {
    uint64_t timestamp_ns;
    uint64_t order_id;
    int64_t price;
    int32_t quantity;
    char symbol[8];
} __attribute__((packed)) sbe_order_add_t;

int main() {
    // Simulated raw network packet byte stream
    uint8_t packet_buffer[256];
    memset(packet_buffer, 0, sizeof(packet_buffer));

    sbe_header_t *hdr = (sbe_header_t *)packet_buffer;
    hdr->block_length = sizeof(sbe_order_add_t);
    hdr->template_id = 101;
    hdr->schema_id = 1;
    hdr->version = 9;

    sbe_order_add_t *body = (sbe_order_add_t *)(packet_buffer + sizeof(sbe_header_t));
    body->timestamp_ns = 1789234567890ULL;
    body->order_id = 88392019ULL;
    body->price = 6542000; // e.g., $65,420.00 fixed point
    body->quantity = 150;
    memcpy(body->symbol, "BTC-USD", 8);

    // Zero-copy parsing directly from raw wire bytes
    sbe_header_t *parsed_hdr = (sbe_header_t *)packet_buffer;
    sbe_order_add_t *parsed_body = (sbe_order_add_t *)(packet_buffer + sizeof(sbe_header_t));

    printf("[+] Zero-Copy SBE Protocol Parser Executed.\n");
    printf("[+] Template ID: %u | Schema ID: %u\n", parsed_hdr->template_id, parsed_hdr->schema_id);
    printf("[+] Decoded Order ID: %lu | Symbol: %.8s | Price: %ld | Qty: %d\n", 
           parsed_body->order_id, parsed_body->symbol, parsed_body->price, parsed_body->quantity);

    return 0;
}
