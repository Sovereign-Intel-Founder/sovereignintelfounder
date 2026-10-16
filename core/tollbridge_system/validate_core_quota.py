import os
import hashlib
from sip_remote_handoff.node_auth import SipHandoffNode

def validate_request_signature(envelope: dict) -> bool:
    """
    Replaces legacy HMAC shared-secret verification with strict 
    Ed25519 asymmetric signature validation via SipHandoffNode.
    """
    node = SipHandoffNode()
    return node.verify_envelope(envelope)

if __name__ == "__main__":
    # Self-test validation stub
    node = SipHandoffNode()
    sample_env = node.create_envelope({"test": "quota_validation"})
    assert validate_request_signature(sample_env) == True, "Asymmetric quota validation failed!"
    print("Core quota validation successfully migrated to Ed25519.")
