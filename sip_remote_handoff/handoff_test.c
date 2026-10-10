#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

int verify_payload(const char* payload, const char* expected_hash) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)payload, strlen(payload), hash);
    char hex_str[65];
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        sprintf(hex_str + (i * 2), "%02x", hash[i]);
    hex_str[64] = 0;
    return strcmp(hex_str, expected_hash) == 0;
}
int main() {
    const char* test_payload = "SovereignIntelligenceProtocol-Payload-2026";
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)test_payload, strlen(test_payload), hash);
    char valid_hash[65];
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) sprintf(valid_hash + (i * 2), "%02x", hash[i]);
    valid_hash[64] = 0;
    if (verify_payload(test_payload, valid_hash)) {
        printf("[+] Cryptographic Handoff: Valid payload signature verified successfully.\n");
    } else {
        fprintf(stderr, "[-] ERROR: Valid payload failed verification!\n");
        return 1;
    }
    if (!verify_payload("Tampered-Payload-Data", valid_hash)) {
        printf("[+] Cryptographic Handoff: Tamper rejection test PASSED (Malformed input dropped).\n");
    } else {
        fprintf(stderr, "[-] ERROR: Tampered payload was incorrectly accepted!\n");
        return 1;
    }
    return 0;
}
