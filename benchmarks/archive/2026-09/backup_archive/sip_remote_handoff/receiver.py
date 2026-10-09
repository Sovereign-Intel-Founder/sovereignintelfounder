import json
import time
from .transport import recv_frame
from envelope import verify_envelope_signature, compute_artifact_sha256

def handle_connection(conn, addr, trusted_keys=None, receiver_node_id=None):
    if trusted_keys is None:
        trusted_keys = {}
    try:
        raw_data = recv_frame(conn)
        try:
            payload = json.loads(raw_data.decode("utf-8"))
        except Exception:
            return {"status": "REJECTED", "reason": "MALFORMED_JSON"}

        if not isinstance(payload, dict):
            return {"status": "REJECTED", "reason": "MALFORMED_JSON"}

        if payload.get("envelope_version") != "sip-transport-v1":
            return {"status": "REJECTED", "reason": "UNSUPPORTED_VERSION"}

        if receiver_node_id and payload.get("receiver_node_id") != receiver_node_id:
            return {"status": "REJECTED", "reason": "INVALID_DESTINATION"}

        now = int(time.time())
        expires_at = payload.get("expires_at", 0)
        created_at = payload.get("created_at", 0)
        if expires_at <= now or created_at > now + 300:
            return {"status": "REJECTED", "reason": "ENVELOPE_EXPIRED"}

        artifact = payload.get("artifact")
        declared_hash = payload.get("artifact_sha256")
        if artifact is not None and declared_hash is not None:
            computed_hash = compute_artifact_sha256(artifact)
            if computed_hash != declared_hash:
                return {"status": "REJECTED", "reason": "HASH_MISMATCH"}

        sender_id = payload.get("sender_node_id")
        if trusted_keys and sender_id not in trusted_keys:
            return {"status": "REJECTED", "reason": "UNKNOWN_SENDER"}

        if trusted_keys and sender_id in trusted_keys:
            sig = payload.get("transport_signature")
            pub_key = trusted_keys[sender_id]
            if not verify_envelope_signature(payload, sig, pub_key):
                return {"status": "REJECTED", "reason": "INVALID_TRANSPORT_SIGNATURE"}

        return {"status": "ACCEPTED"}
    except Exception as e:
        return {"status": "REJECTED", "reason": str(e)}
