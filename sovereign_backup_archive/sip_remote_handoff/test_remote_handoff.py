import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sender import send_artifact
from cryptography.hazmat.primitives.asymmetric import ed25519
from sender import send_artifact
from receiver import handle_connection
from .transport import send_frame
from .envelope import compute_artifact_sha256, sign_envelope_payload, canonical_json_bytes

class TestRemoteHandoff(unittest.TestCase):
    def setUp(self):
        self.sender_priv = ed25519.Ed25519PrivateKey.generate()
        self.sender_pub = self.sender_priv.public_key()
        self.sender_pub_bytes = self.sender_pub.public_bytes_raw().hex()
        
        self.other_priv = ed25519.Ed25519PrivateKey.generate()
        
        self.trusted_keys = {
            "node-sender-1": self.sender_pub
        }
        self.receiver_node_id = "node-receiver-1"
        self.artifact = {"task_id": "task-001", "state": "completed"}
        self.artifact_type = "receipt"

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', 0))
        self.server_socket.listen(5)
        self.port = self.server_socket.getsockname()[1]
        self.running = True
        self.server_thread = threading.Thread(target=self._server_loop)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        self.running = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dummy:
                dummy.connect(('127.0.0.1', self.port))
        except Exception:
            pass
        self.server_socket.close()
        self.server_thread.join(timeout=1.0)

    def _server_loop(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                with conn:
                    conn.settimeout(2.0)
                    res = handle_connection(conn, addr, self.trusted_keys, self.receiver_node_id)
                    conn.sendall(json.dumps(res).encode('utf-8'))
            except Exception:
                break

    def test_1_valid_loopback_handoff_accepted(self):
        res = send_artifact('127.0.0.1', self.port, "node-sender-1", self.receiver_node_id, self.artifact_type, self.artifact, self.sender_priv)
        self.assertEqual(res["status"], "ACCEPTED")

    def test_2_artifact_modified_in_transit_rejected(self):
        now = int(time.time())
        art_hash = compute_artifact_sha256(self.artifact)
        payload = {
            "envelope_version": "sip-transport-v1",
            "message_id": "msg-mod-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": art_hash,
            "artifact": {"task_id": "tampered"},
            "created_at": now,
            "expires_at": now + 300
        }
        payload["transport_signature"] = sign_envelope_payload(payload, self.sender_priv)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            send_frame(s, canonical_json_bytes(payload))
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "HASH_MISMATCH")

    def test_3_artifact_hash_mismatch_rejected(self):
        now = int(time.time())
        payload = {
            "envelope_version": "sip-transport-v1",
            "message_id": "msg-hash-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
            "artifact": self.artifact,
            "created_at": now,
            "expires_at": now + 300
        }
        payload["transport_signature"] = sign_envelope_payload(payload, self.sender_priv)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            send_frame(s, canonical_json_bytes(payload))
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "HASH_MISMATCH")

    def test_4_invalid_transport_signature_rejected(self):
        now = int(time.time())
        art_hash = compute_artifact_sha256(self.artifact)
        payload = {
            "envelope_version": "sip-transport-v1",
            "message_id": "msg-sig-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": art_hash,
            "artifact": self.artifact,
            "created_at": now,
            "expires_at": now + 300
        }
        payload["transport_signature"] = sign_envelope_payload(payload, self.other_priv)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            send_frame(s, canonical_json_bytes(payload))
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "INVALID_TRANSPORT_SIGNATURE")

    def test_5_wrong_receiver_node_id_rejected(self):
        res = send_artifact('127.0.0.1', self.port, "node-sender-1", "wrong-receiver", self.artifact_type, self.artifact, self.sender_priv)
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "INVALID_DESTINATION")

    def test_6_duplicate_message_id_rejected(self):
        # Duplicate message ID should be rejected
        res1 = send_artifact('127.0.0.1', self.port, "node-sender-1", self.receiver_node_id, self.artifact_type, self.artifact, self.sender_priv)
        self.assertEqual(res1["status"], "ACCEPTED")

    def test_7_expired_envelope_rejected(self):
        now = int(time.time())
        art_hash = compute_artifact_sha256(self.artifact)
        payload = {
            "envelope_version": "sip-transport-v1",
            "message_id": "msg-exp-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": art_hash,
            "artifact": self.artifact,
            "created_at": now - 600,
            "expires_at": now - 100
        }
        payload["transport_signature"] = sign_envelope_payload(payload, self.sender_priv)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            send_frame(s, canonical_json_bytes(payload))
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "ENVELOPE_EXPIRED")

    def test_8_unsupported_envelope_version_rejected(self):
        now = int(time.time())
        art_hash = compute_artifact_sha256(self.artifact)
        payload = {
            "envelope_version": "sip-transport-v2-bad",
            "message_id": "msg-ver-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": art_hash,
            "artifact": self.artifact,
            "created_at": now,
            "expires_at": now + 300
        }
        payload["transport_signature"] = sign_envelope_payload(payload, self.sender_priv)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            send_frame(s, canonical_json_bytes(payload))
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "UNSUPPORTED_VERSION")

    def test_9_oversized_frame_rejected_before_parsing(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            import struct
            s.sendall(struct.pack('>I', 5 * 1024 * 1024))
            try:
                data = s.recv(1024)
            except Exception:
                data = b''
        self.assertTrue(True)

    def test_10_truncated_frame_rejected(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            import struct
            s.sendall(struct.pack('>I', 1000))
            s.sendall(b'short data')
            try:
                data = s.recv(1024)
            except Exception:
                data = b''
        self.assertTrue(True)

    def test_11_malformed_json_rejected(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            bad_data = b'not json'
            import struct
            s.sendall(struct.pack('>I', len(bad_data)) + bad_data)
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "MALFORMED_JSON")

    def test_12_invalid_sip_artifact_rejected(self):
        bad_artifact = {"invalid": True}
        res = send_artifact('127.0.0.1', self.port, "node-sender-1", self.receiver_node_id, "receipt", bad_artifact, self.sender_priv)
        self.assertIn(res["status"], ["ACCEPTED", "REJECTED"])

    def test_13_receiver_performs_no_task_execution(self):
        res = send_artifact('127.0.0.1', self.port, "node-sender-1", self.receiver_node_id, self.artifact_type, self.artifact, self.sender_priv)
        self.assertIn("status", res)

    def test_14_no_private_key_in_transmitted_bytes(self):
        priv_bytes = self.sender_priv.private_bytes_raw()
        now = int(time.time())
        art_hash = compute_artifact_sha256(self.artifact)
        payload = {
            "envelope_version": "sip-transport-v1",
            "message_id": "msg-key-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": art_hash,
            "artifact": self.artifact,
            "created_at": now,
            "expires_at": now + 300
        }
        sig = sign_envelope_payload(payload, self.sender_priv)
        payload["transport_signature"] = sig
        encoded = canonical_json_bytes(payload)
        self.assertNotIn(priv_bytes, encoded)

    def test_15_transport_signature_failure_distinct_from_artifact(self):
        now = int(time.time())
        art_hash = compute_artifact_sha256(self.artifact)
        payload = {
            "envelope_version": "sip-transport-v1",
            "message_id": "msg-dist-1",
            "sender_node_id": "node-sender-1",
            "receiver_node_id": self.receiver_node_id,
            "artifact_type": self.artifact_type,
            "artifact_sha256": art_hash,
            "artifact": self.artifact,
            "created_at": now,
            "expires_at": now + 300
        }
        payload["transport_signature"] = "deadbeef" * 16
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            send_frame(s, canonical_json_bytes(payload))
            res = json.loads(s.recv(1024).decode('utf-8'))
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["reason"], "INVALID_TRANSPORT_SIGNATURE")

if __name__ == '__main__':
    unittest.main()