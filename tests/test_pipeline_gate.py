import os
from sip_remote_handoff.node_auth import SipHandoffNode
from sip_remote_handoff.pipeline_gate import ExecutionPipelineGate

def test_pipeline_ingestion():
    node = SipHandoffNode(key_path="test_pipeline_key.bin")
    gate = ExecutionPipelineGate(node)

    # 1. Valid envelope should pass ingestion
    valid_env = node.create_envelope({"action": "execute_task", "id": 101})
    assert gate.ingest(valid_env) == True, "Pipeline gate rejected a valid envelope!"

    # 2. Tampered envelope should be dropped at the gate
    bad_env = valid_env.copy()
    bad_env["payload"] = {"action": "malicious_injection", "id": 101}
    assert gate.ingest(bad_env) == False, "Pipeline gate accepted a tampered envelope!"

    # 3. Local override should allow administrative override
    os.environ["SIP_LOCAL_OVERRIDE"] = "1"
    assert gate.ingest(bad_env) == True, "Pipeline gate failed to respect local override!"

    # Cleanup
    if os.path.exists("test_pipeline_key.bin"):
        os.remove("test_pipeline_key.bin")
    del os.environ["SIP_LOCAL_OVERRIDE"]
    print("Pipeline gate tests passed cleanly.")
