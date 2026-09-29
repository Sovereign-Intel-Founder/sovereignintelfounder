import unittest
from core.mesh.execution.verifier import EvidenceReturn
import hashlib
import json

class TestResultVerifier(unittest.TestCase):

    def test_valid_evidence_verification(self):
        result_data = {"status": "SUCCESS", "metrics": {"cycles": 1024, "latency_ns": 450}}
        canonical_payload = json.dumps(result_data, sort_keys=True, separators=(',', ':'))
        valid_hash = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()

        evidence = EvidenceReturn(
            task_id="task-001",
            participant_id="node-worker-epyc-01",
            result_data=result_data,
            output_hash=valid_hash,
            signature="mock-signature-bytes"
        )

        self.assertTrue(evidence.verify_integrity())

    def test_tampered_evidence_rejection(self):
        original_data = {"status": "SUCCESS", "metrics": {"cycles": 1024}}
        canonical_payload = json.dumps(original_data, sort_keys=True, separators=(',', ':'))
        original_hash = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()

        # Tampered data payload
        tampered_data = {"status": "SUCCESS", "metrics": {"cycles": 999999}}

        evidence = EvidenceReturn(
            task_id="task-001",
            participant_id="node-worker-epyc-01",
            result_data=tampered_data,
            output_hash=original_hash, # Mismatched hash
            signature="mock-signature-bytes"
        )

        self.assertFalse(evidence.verify_integrity())

if __name__ == "__main__":
    unittest.main()
