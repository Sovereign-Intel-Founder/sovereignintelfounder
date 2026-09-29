import unittest
import hashlib
import json
from core.mesh.registration.schema import ParticipantRegistration
from core.mesh.indexing.index import CapabilityIndex
from core.mesh.matching.matcher import JobTask
from core.mesh.execution.verifier import EvidenceReturn
from core.mesh.orchestrator import MeshPipeline

class TestMeshPipeline(unittest.TestCase):

    def setUp(self):
        self.index = CapabilityIndex()
        self.pipeline = MeshPipeline(self.index)

        # Register a valid worker
        self.reg = ParticipantRegistration(
            participant_id="node-worker-epyc-01",
            public_key_pem="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...\n-----END PUBLIC KEY-----",
            supported_caps=["compute:vector:avx512"],
            endpoint_uri="grpc://127.0.0.1:9092",
            nonce=1,
            signature="a" * 64
        )
        self.index.register(self.reg)

    def test_successful_pipeline_execution(self):
        task = JobTask(
            task_id="task-100",
            required_caps=["compute:vector:avx512"],
            payload_ref="ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        )

        result_data = {"status": "SUCCESS", "output": 42}
        canonical_payload = json.dumps(result_data, sort_keys=True, separators=(',', ':'))
        valid_hash = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()

        evidence = EvidenceReturn(
            task_id="task-100",
            participant_id="node-worker-epyc-01",
            result_data=result_data,
            output_hash=valid_hash,
            signature="mock-sig"
        )

        self.assertTrue(self.pipeline.dispatch_and_verify(task, evidence))

    def test_pipeline_rejection_on_mismatched_participant(self):
        task = JobTask(
            task_id="task-101",
            required_caps=["compute:vector:avx512"],
            payload_ref="ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        )

        result_data = {"status": "SUCCESS", "output": 42}
        canonical_payload = json.dumps(result_data, sort_keys=True, separators=(',', ':'))
        valid_hash = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()

        # Evidence submitted by a rogue/unauthorized node ID
        evidence = EvidenceReturn(
            task_id="task-101",
            participant_id="node-rogue-fake-99",
            result_data=result_data,
            output_hash=valid_hash,
            signature="mock-sig"
        )

        self.assertFalse(self.pipeline.dispatch_and_verify(task, evidence))

if __name__ == "__main__":
    unittest.main()
