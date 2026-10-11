from cryptography.hazmat.primitives import serialization
import unittest
import base64
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from sovereign.core.node_control_plane import NodeControlPlane

class TestNodeControlIntegration(unittest.TestCase):
    def setUp(self):
        self.control = NodeControlPlane(ledger_path="core/data/test_control.db")
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key_bytes = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        self.public_key_hex = self.public_key_bytes.hex()

    def sign_message(self, message_dict: dict) -> str:
        message_bytes = json.dumps(message_dict, sort_keys=True).encode()
        sig = self.private_key.sign(message_bytes)
        return base64.b64encode(sig).decode()

    def test_valid_enrollment_and_heartbeat(self):
        msg = {"action": "enroll", "timestamp": 1728320000}
        payload = {
            "public_key": self.public_key_hex,
            "signature": self.sign_message(msg),
            "message": msg
        }
        res = self.control.process_enrollment(payload)
        self.assertEqual(res["status"], "SUCCESS")

        hb_msg = {"sequence": 1, "status": "active"}
        hb_payload = {
            "public_key": self.public_key_hex,
            "signature": self.sign_message(hb_msg),
            "message": hb_msg
        }
        hb_res = self.control.process_heartbeat(hb_payload)
        self.assertEqual(hb_res["status"], "ACK")
        self.assertEqual(hb_res["sequence"], 1)

    def test_invalid_signature_rejection(self):
        msg = {"action": "enroll", "timestamp": 1728320000}
        payload = {
            "public_key": self.public_key_hex,
            "signature": "dGhpc2lzZmFrZXNpZ25hdHVyZQ==",
            "message": msg
        }
        res = self.control.process_enrollment(payload)
        self.assertEqual(res["status"], "REJECTED")

if __name__ == "__main__":
    unittest.main()
