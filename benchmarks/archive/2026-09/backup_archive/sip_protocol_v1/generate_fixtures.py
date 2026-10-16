import json
import os

FIXTURES_DIR = "sip_protocol_v1/fixtures"
os.makedirs(FIXTURES_DIR, exist_ok=True)

def write_fixture(filename, data):
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True, indent=2)
    print(f"Generated fixture: {path}")

# 1. Valid Task Manifest
manifest = {
    "schema": "sip.task_manifest.v1",
    "task_id": "12345678-1234-5678-1234-567812345678",
    "task_type": "file_hash_verification",
    "input_commitment": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "created_at": "2026-09-24T02:00:00.000Z"
}
write_fixture("valid_manifest.json", manifest)

# 2. Valid Capsule Checkpoint
checkpoint = {
    "schema": "sip.capsule_checkpoint.v1",
    "capsule_id": "87654321-4321-8765-4321-876543218765",
    "task_id": "12345678-1234-5678-1234-567812345678",
    "sequence_number": 1,
    "state_hash": "cf23df2207d99a74fbe169e3eba035e633b65d947b0c407150033ad88f01bba2",
    "nonce": "abcdef0123456789",
    "created_at": "2026-09-24T02:05:00.000Z"
}
write_fixture("valid_checkpoint.json", checkpoint)

# 3. Valid Execution Receipt
receipt = {
    "schema": "sip.execution_receipt.v1",
    "receipt_id": "11112222-3333-4444-5555-666677778888",
    "capsule_id": "87654321-4321-8765-4321-876543218765",
    "sequence_number": 1,
    "source_cell_id": "cell_alpha",
    "destination_cell_id": "cell_beta",
    "prev_receipt_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    "state_hash": "cf23df2207d99a74fbe169e3eba035e633b65d947b0c407150033ad88f01bba2",
    "result_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "nonce": "abcdef0123456789",
    "expires_at": "2026-09-24T03:00:00.000Z",
    "created_at": "2026-09-24T02:06:00.000Z",
    "public_key": "4a5c89f0123456789abcdef0123456789abcdef0123456789abcdef012345678",
    "signature": "c9839971489379872349872394872394872394872394872394872394872394872394872394872394872394872394872394872394872394872394872394872394"
}
write_fixture("valid_receipt.json", receipt)

# Adversarial Fixtures Mapped to Gates
adversarial_cases = [
    ("adv_altered_state.json", {"state_hash": "0000000000000000000000000000000000000000000000000000000000000000"}, "commitment_mismatch"),
    ("adv_altered_input.json", {"input_commitment": "0000000000000000000000000000000000000000000000000000000000000000"}, "commitment_mismatch"),
    ("adv_altered_destination.json", {"destination_cell_id": "unauthorized_cell"}, "destination_unauthorized"),
    ("adv_altered_nonce.json", {"nonce": "bad_nonce_value_0"}, "nonce_reused"),
    ("adv_altered_sequence.json", {"sequence_number": 999}, "sequence_invalid"),
    ("adv_altered_prev_hash.json", {"prev_receipt_hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"}, "lineage_invalid"),
    ("adv_expired.json", {"expires_at": "2020-01-01T00:00:00.000Z"}, "capsule_expired"),
    ("adv_revoked.json", {"source_cell_id": "revoked_cell_id"}, "cell_revoked"),
    ("adv_invalid_signature.json", {"signature": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"}, "signature_invalid"),
    ("adv_replayed_checkpoint.json", {"nonce": "replayed_nonce_xyz"}, "nonce_reused")
]

for filename, mutation, expected_code in adversarial_cases:
    mutated = dict(receipt)
    mutated.update(mutation)
    mutated["expected_rejection_code"] = expected_code
    write_fixture(filename, mutated)

print("All conformance fixtures generated successfully.")
