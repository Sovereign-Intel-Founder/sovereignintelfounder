import sys, json
from sip_remote_handoff.node_auth import SipHandoffNode

def run_phase_one():
    node = SipHandoffNode()
    checks = []
    
    has_keys = node.private_key and node.public_key
    checks.append({
        "phase": 1, 
        "check": "awake.process", 
        "organ": "awake", 
        "status": "pass" if has_keys else "fail", 
        "evidence": "Keypair active"
    })
    
    checks.append({
        "phase": 1, 
        "check": "identity.declare", 
        "organ": "identity", 
        "status": "pass" if node.node_id != "unbound" else "fail", 
        "evidence": f"Node ID: {node.node_id}"
    })
    
    try:
        verified = node.verify_envelope(node.create_envelope({"audit": "live"}))
        checks.append({
            "phase": 1, 
            "check": "audit.chain_valid", 
            "organ": "audit", 
            "status": "pass" if verified else "fail", 
            "evidence": "Verified"
        })
    except Exception as e:
        checks.append({
            "phase": 1, 
            "check": "audit.chain_valid", 
            "organ": "audit", 
            "status": "fail", 
            "evidence": str(e)
        })
        
    return checks

if __name__ == "__main__":
    for c in run_phase_one():
        print(json.dumps(c))
        sys.stdout.flush()
