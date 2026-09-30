import unittest
from core.mesh.registration.schema import ParticipantRegistration, RegistrationValidationError

class TestParticipantRegistrationSchema(unittest.TestCase):
    
    def setUp(self):
        self.valid_payload = {
            "participant_id": "node-worker-epyc-01",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...\n-----END PUBLIC KEY-----",
            "supported_caps": ["compute:vector:avx512", "memory:numa:isolated"],
            "endpoint_uri": "grpc://127.0.0.1:9092",
            "nonce": 1727635840,
            "signature": "a" * 64
        }

    def test_valid_registration(self):
        reg = ParticipantRegistration(**self.valid_payload)
        self.assertEqual(reg.participant_id, "node-worker-epyc-01")
        self.assertEqual(len(reg.supported_caps), 2)
        fingerprint = reg.compute_fingerprint()
        self.assertEqual(len(fingerprint), 64)

    def test_invalid_participant_id(self):
        self.valid_payload["participant_id"] = "invalid id with spaces!"
        with self.assertRaises(RegistrationValidationError):
            ParticipantRegistration(**self.valid_payload)

    def test_invalid_endpoint_scheme(self):
        self.valid_payload["endpoint_uri"] = "http://unsafe-endpoint.com"
        with self.assertRaises(RegistrationValidationError):
            ParticipantRegistration(**self.valid_payload)

    def test_empty_capabilities(self):
        self.valid_payload["supported_caps"] = []
        with self.assertRaises(RegistrationValidationError):
            ParticipantRegistration(**self.valid_payload)

if __name__ == "__main__":
    unittest.main()
