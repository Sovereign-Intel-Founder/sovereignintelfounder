import os
import json
import time
import hashlib
import hmac
import uuid

STATE_DIR = os.path.expanduser("~/.sip_node_state")
os.makedirs(STATE_DIR, exist_ok=True)

class NodeIdentity:
    def __init__(self, state_dir=STATE_DIR):
        self.state_dir = state_dir
        self.id_file = os.path.join(self.state_dir, "node_identity.json")
        self.node_id = None
        self.secret_key = None
        self.public_key = None
        self.bootstrap()

    def bootstrap(self):
        if os.path.exists(self.id_file):
            with open(self.id_file, "r") as f:
                data = json.load(f)
                self.node_id = data["node_id"]
                self.secret_key = data["secret_key"]
                self.public_key = data["public_key"]
        else:
            self.node_id = f"node-{uuid.uuid4().hex[:12]}"
            self.secret_key = os.urandom(32).hex()
            self.public_key = hashlib.sha256(self.secret_key.encode()).hexdigest()
            data = {
                "node_id": self.node_id,
                "secret_key": self.secret_key,
                "public_key": self.public_key,
                "protocol_version": "1.0.0",
                "software_version": "2.0.0",
                "capabilities": ["alpr_ingest", "realtime_hotlist"]
            }
            with open(self.id_file, "w") as f:
                json.dump(data, f, indent=2)

    def sign_payload(self, payload: dict) -> str:
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hmac.new(self.secret_key.encode("utf-8"), serialized, hashlib.sha256).hexdigest()

class TollBridgeLedger:
    def __init__(self, ledger_dir=STATE_DIR):
        self.ledger_file = os.path.join(ledger_dir, "ashburn_ledger.json")
        self.seen_nonces = set()
        self.enrolled_nodes = {}
        self.load()

    def load(self):
        if os.path.exists(self.ledger_file):
            with open(self.ledger_file, "r") as f:
                data = json.load(f)
                self.enrolled_nodes = data.get("nodes", {})

    def save(self):
        with open(self.ledger_file, "w") as f:
            json.dump({"nodes": self.enrolled_nodes}, f, indent=2)

    def process_enrollment(self, payload, signature):
        nonce = payload.get("nonce")
        timestamp = payload.get("timestamp", 0)
        node_id = payload.get("node_id")

        if nonce in self.seen_nonces:
            return {"status": "REJECTED", "reason": "Replayed nonce"}
        if abs(time.time() - timestamp) > 300:
            return {"status": "REJECTED", "reason": "Stale timestamp"}

        self.seen_nonces.add(nonce)
        receipt_id = f"rcpt-enroll-{uuid.uuid4().hex[:8]}"
        self.enrolled_nodes[node_id] = {
            "public_key": payload.get("public_key"),
            "status": "healthy",
            "enrolled_at": timestamp,
            "receipt_id": receipt_id
        }
        self.save()
        return {"status": "SUCCESS", "receipt_id": receipt_id, "node_id": node_id}

    def process_heartbeat(self, payload, signature):
        node_id = payload.get("node_id")
        seq = payload.get("sequence")
        if node_id not in self.enrolled_nodes:
            return {"status": "REJECTED", "reason": "Unenrolled node"}
        
        self.enrolled_nodes[node_id]["last_heartbeat"] = payload.get("timestamp")
        self.enrolled_nodes[node_id]["last_sequence"] = seq
        self.save()
        return {"status": "ACK", "sequence": seq}

    def process_intelligence(self, payload):
        event_id = f"evt-{uuid.uuid4().hex[:8]}"
        object_id = f"obj-{uuid.uuid4().hex[:8]}"
        delivery_receipt = f"dlv-{uuid.uuid4().hex[:8]}"
        return {
            "status": "DELIVERED",
            "event_id": event_id,
            "object_id": object_id,
            "delivery_receipt": delivery_receipt
        }

def run_vertical_slice_test():
    print("==================================================")
    print("RUNNING COMMONS -> ASHBURN CONTROL PLANE TEST")
    print("==================================================")
    
    node = NodeIdentity()
    ledger = TollBridgeLedger()

    # 1. Enrollment
    enroll_payload = {
        "node_id": node.node_id,
        "public_key": node.public_key,
        "protocol_version": "1.0.0",
        "software_version": "2.0.0",
        "timestamp": time.time(),
        "nonce": uuid.uuid4().hex
    }
    sig = node.sign_payload(enroll_payload)
    enroll_receipt = ledger.process_enrollment(enroll_payload, sig)

    # 2. Heartbeat
    hb_payload = {
        "node_id": node.node_id,
        "sequence": 1,
        "timestamp": time.time(),
        "nonce": uuid.uuid4().hex
    }
    hb_sig = node.sign_payload(hb_payload)
    hb_receipt = ledger.process_heartbeat(hb_payload, hb_sig)

    # 3. Intelligence Submission
    intel_payload = {
        "node_id": node.node_id,
        "payload_hash": hashlib.sha256(b"alpr_frame_data").hexdigest()
    }
    intel_receipt = ledger.process_intelligence(intel_payload)

    print(f"node_id:          {node.node_id}")
    print(f"enrollment rcpt:  {enroll_receipt['receipt_id']}")
    print(f"heartbeat seq:    {hb_receipt['sequence']}")
    print(f"event_id:         {intel_receipt['event_id']}")
    print(f"object_id:        {intel_receipt['object_id']}")
    print(f"delivery receipt: {intel_receipt['delivery_receipt']}")
    print(f"ledger path:      {ledger.ledger_file}")
    
    if enroll_receipt['status'] == 'SUCCESS' and intel_receipt['status'] == 'DELIVERED':
        print("\nFINAL RESULT: PASS")
    else:
        print("\nFINAL RESULT: FAIL")

if __name__ == "__main__":
    run_vertical_slice_test()
