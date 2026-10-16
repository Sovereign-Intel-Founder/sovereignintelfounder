import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from envelope import canonical_json_bytes, compute_artifact_sha256, sign_envelope_payload

def send_artifact(host: str, port: int, sender_node_id: str, receiver_node_id: str, artifact_type: str, artifact: dict, private_key, expires_in_sec: int = 300) -> dict:
    now = int(time.time())
    message_id = str(uuid.uuid4())
    art_hash = compute_artifact_sha256(artifact)

    payload = {
        "envelope_version": "sip-transport-v1",
        "message_id": message_id,
        "sender_node_id": sender_node_id,
        "receiver_node_id": receiver_node_id,
        "artifact_type": artifact_type,
        "artifact_sha256": art_hash,
        "artifact": artifact,
        "created_at": now,
        "expires_at": now + expires_in_sec
    }

    sig = sign_envelope_payload(payload, private_key)
    envelope = dict(payload)
    envelope["transport_signature"] = sig

    envelope_bytes = canonical_json_bytes(envelope)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        send_frame(s, envelope_bytes)
        response_bytes = s.recv(4096)
        import json
        return json.loads(response_bytes.decode('utf-8'))