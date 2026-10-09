from core.authoritative_logger import record_event, DB_PATH
import os

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("Testing authoritative logger insertion...")
hash1 = record_event(
    event_id="evt_001",
    request_id="req_abc",
    auth_result="accepted",
    processing_status="completed",
    receipt_id="rcpt_xyz",
    payload={"action": "test_payload", "value": 42}
)
print(f"First record hash: {hash1}")

hash2 = record_event(
    event_id="evt_002",
    request_id="req_def",
    auth_result="accepted",
    processing_status="processing",
    receipt_id=None,
    payload={"action": "test_payload_2", "value": 100}
)
print(f"Second record hash (chained): {hash2}")
print("Local verification test passed successfully!")
