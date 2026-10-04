#ifndef SIP_HANDOFF_VERIFY_H
#ifndef SIP_HANDOFF_VERIFY_H
#define SIP_HANDOFF_VERIFY_H

#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>

// Validates incoming SHA-256 digest against raw payload buffer
static inline int verify_sip_envelope(const char *payload, size_t len, const unsigned char *expected_hash) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int md_len;
    
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) return 0;

    if (1 != EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) ||
        1 != EVP_DigestUpdate(ctx, payload, len) ||
        1 != EVP_DigestFinal_ex(ctx, hash, &md_len)) {
        EVP_MD_CTX_free(ctx);
        return 0;
    }
    EVP_MD_CTX_free(ctx);

    return (memcmp(hash, expected_hash, 32) == 0);
}

#endif
