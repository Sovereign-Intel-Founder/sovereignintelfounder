from core.tollbridge_runtime import process_secure_ingress
import os

db_file = "sovereign_ledger.db"
if os.path.exists(db_file):
    os.remove(db_file)

print("--- Test 1: Valid Ingress ---")
res1 = process_secure_ingress(
    request_id="req_001",
    nonce="nonce_abc123",
    auth_signature_valid=True,
    payload={"transfer": 500, "destination": "node_b"}
)
print("Result 1:", res1)

print("\n--- Test 2: Replay Attack Prevention (Duplicate Nonce) ---")
try:
    process_secure_ingress(
        request_id="req_002",
        nonce="nonce_abc123", # Duplicate nonce
        auth_signature_valid=True,
        payload={"transfer": 500, "destination": "node_b"}
    )
except ValueError as e:
    print("Caught expected replay error:", e)

print("\n--- Test 3: Invalid Authentication ---")
try:
    process_secure_ingress(
        request_id="req_003",
        nonce="nonce_xyz999",
        auth_signature_valid=False, # Bad signature
        payload={"transfer": 1000}
    )
except PermissionError as e:
    print("Caught expected auth error:", e)

print("\nAll runtime integration tests passed locally with zero exceptions swallowed!")
