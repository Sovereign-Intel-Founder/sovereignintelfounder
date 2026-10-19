import os
from sip_remote_handoff.node_auth import SipHandoffNode

def test_handoff_lifecycle():
    node = SipHandoffNode(key_path="test_node_key.bin")
    
    envelope = node.create_envelope({"task": "sync_state", "nonce": 42})
    assert node.verify_envelope(envelope) == True, "Valid envelope failed verification!"

    tampered_envelope = envelope.copy()
    tampered_envelope["payload"] = {"task": "malicious_action", "nonce": 42}
    assert node.verify_envelope(tampered_envelope) == False, "Tampered envelope was incorrectly accepted!"

    os.environ["SIP_LOCAL_OVERRIDE"] = "1"
    assert node.verify_envelope(tampered_envelope) == True, "Local override failed to bypass check!"
    
    if os.path.exists("test_node_key.bin"):
        os.remove("test_node_key.bin")
    del os.environ["SIP_LOCAL_OVERRIDE"]
    print("Stage 1 Handoff tests passed cleanly.")
