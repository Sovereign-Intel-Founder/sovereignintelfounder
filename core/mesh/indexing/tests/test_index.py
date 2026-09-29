import unittest
from core.mesh.registration.schema import ParticipantRegistration
from core.mesh.indexing.index import CapabilityIndex

class TestCapabilityIndex(unittest.TestCase):
    
    def setUp(self):
        self.index = CapabilityIndex()
        self.reg1 = ParticipantRegistration(
            participant_id="node-worker-01",
            public_key_pem="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...\n-----END PUBLIC KEY-----",
            supported_caps=["compute:vector:avx512", "memory:numa:isolated"],
            endpoint_uri="grpc://127.0.0.1:9092",
            nonce=1,
            signature="a" * 64
        )
        self.reg2 = ParticipantRegistration(
            participant_id="node-worker-02",
            public_key_pem="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...\n-----END PUBLIC KEY-----",
            supported_caps=["compute:vector:avx512", "net:bypass:af_xdp"],
            endpoint_uri="grpc://127.0.0.1:9093",
            nonce=2,
            signature="b" * 64
        )

    def test_registration_and_lookup(self):
        self.index.register(self.reg1)
        self.index.register(self.reg2)

        # Single cap present on both
        matches = self.index.find_matching_participants(["compute:vector:avx512"])
        self.assertEqual(matches, ["node-worker-01", "node-worker-02"])

        # Intersection cap present on only one
        matches = self.index.find_matching_participants(["compute:vector:avx512", "memory:numa:isolated"])
        self.assertEqual(matches, ["node-worker-01"])

        # Non-existent cap
        matches = self.index.find_matching_participants(["nonexistent:capability"])
        self.assertEqual(matches, [])

    def test_unregister(self):
        self.index.register(self.reg1)
        self.assertEqual(self.index.find_matching_participants(["memory:numa:isolated"]), ["node-worker-01"])
        
        self.index.unregister("node-worker-01")
        self.assertEqual(self.index.find_matching_participants(["memory:numa:isolated"]), [])
        self.assertIsNone(self.index.get_participant("node-worker-01"))

if __name__ == "__main__":
    unittest.main()
