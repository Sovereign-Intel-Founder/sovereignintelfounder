import unittest
from core.mesh.registration.schema import ParticipantRegistration
from core.mesh.indexing.index import CapabilityIndex
from core.mesh.matching.matcher import JobTask, JobMatcher

class TestJobMatcher(unittest.TestCase):
    
    def setUp(self):
        self.index = CapabilityIndex()
        self.matcher = JobMatcher(self.index)
        
        self.reg = ParticipantRegistration(
            participant_id="node-worker-epyc-01",
            public_key_pem="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...\n-----END PUBLIC KEY-----",
            supported_caps=["compute:vector:avx512", "memory:numa:isolated"],
            endpoint_uri="grpc://127.0.0.1:9092",
            nonce=1,
            signature="a" * 64
        )
        self.index.register(self.reg)

    def test_successful_job_matching(self):
        task = JobTask(
            task_id="task-001",
            required_caps=["compute:vector:avx512"],
            payload_ref="ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        )
        assigned_node = self.matcher.schedule_job(task)
        self.assertEqual(assigned_node, "node-worker-epyc-01")

    def test_failed_job_matching_due_to_missing_capability(self):
        task = JobTask(
            task_id="task-002",
            required_caps=["net:bypass:af_xdp"],
            payload_ref="ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        )
        assigned_node = self.matcher.schedule_job(task)
        self.assertIsNone(assigned_node)

if __name__ == "__main__":
    unittest.main()
