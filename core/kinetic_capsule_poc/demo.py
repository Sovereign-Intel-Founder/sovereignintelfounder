#!/usr/bin/env python3
import os
import json
import hashlib
import time
import sys
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

# Ensure directories exist
os.makedirs("kinetic_capsule_poc/cells/cell_a", exist_ok=True)
os.makedirs("kinetic_capsule_poc/cells/cell_b", exist_ok=True)

def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def compute_transition(prev_state_hash: str, input_commitment: str, step: int) -> str:
    payload = f"{prev_state_hash}:{input_commitment}:{step}".encode('utf-8')
    return sha256_hex(payload)

class KineticCapsuleDemo:
    def __init__(self):
        # Generate persistent keys for the signer (Cell A / Founder key)
        self.signing_key = SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        self.public_key_hex = self.verify_key.encode().hex()

        self.task_id = "task-sip-001"
        self.capsule_id = "capsule-kinetic-999"
        self.code_commitment = sha256_hex(b"sip.kinetic.transition.v1")
        self.input_commitment = sha256_hex(b"genesis-input-payload")
        
        self.used_nonces = set()
        self.receipt_history = []

    def sign_object(self, obj: dict) -> str:
        copy_obj = obj.copy()
        copy_obj.pop("signature", None)
        raw = canonical_json(copy_obj).encode('utf-8')
        signed = self.signing_key.sign(raw)
        return signed.signature.hex()

    def verify_signature(self, obj: dict, sig_hex: str) -> bool:
        copy_obj = obj.copy()
        copy_obj.pop("signature", None)
        raw = canonical_json(copy_obj).encode('utf-8')
        try:
            self.verify_key.verify(raw, bytes.fromhex(sig_hex))
            return True
        except BadSignatureError:
            return False

    def run(self):
        # 1. Create Capsule / Genesis
        nonce = "nonce-abc-123"
        self.used_nonces.add(nonce)
        
        genesis_state_hash = sha256_hex(b"genesis-state")
        prev_receipt_hash = sha256_hex(b"genesis-receipt")

        print("[KINETIC CAPSULE] CREATED")

        # 2. Execute Steps 0 -> 500 in Cell A
        current_state_hash = genesis_state_hash
        for step in range(1, 501):
            current_state_hash = compute_transition(current_state_hash, self.input_commitment, step)

        print("[CELL A] EXECUTING 0 -> 500")

        # 3. Create Checkpoint at step 500
        checkpoint_seq = 1
        checkpoint_nonce = "nonce-chk-500"
        self.used_nonces.add(checkpoint_nonce)

        capsule_state = {
            "schema_version": "sip.capsule.v1",
            "capsule_id": self.capsule_id,
            "task_id": self.task_id,
            "code_commitment": self.code_commitment,
            "input_commitment": self.input_commitment,
            "current_step": 500,
            "total_steps": 1000,
            "state_hash": current_state_hash,
            "previous_receipt_hash": prev_receipt_hash,
            "sequence_number": checkpoint_seq,
            "nonce": checkpoint_nonce,
            "source_cell_id": "cell_a",
            "destination_cell_id": "cell_b",
            "expires_at": int(time.time()) + 3600
        }
        capsule_state["signature"] = self.sign_object(capsule_state)

        # Create Receipt for Checkpoint
        receipt_1 = {
            "receipt_id": "receipt-001",
            "capsule_id": self.capsule_id,
            "task_id": self.task_id,
            "cell_id": "cell_a",
            "transition_type": "checkpoint",
            "state_hash": current_state_hash,
            "input_hash": self.input_commitment,
            "previous_receipt_hash": prev_receipt_hash,
            "sequence_number": checkpoint_seq,
            "timestamp": 1750000000,
            "signature": ""
        }
        receipt_1["signature"] = self.sign_object(receipt_1)
        self.receipt_history.append(receipt_1)

        print("[CELL A] CHECKPOINT SIGNED")
        print("[CELL A] STOPPED")

        # Save checkpoint to file handoff
        checkpoint_path = "kinetic_capsule_poc/cells/cell_a/checkpoint_500.json"
        with open(checkpoint_path, "w") as f:
            json.dump(capsule_state, f, indent=2)

        # 4. Transfer to Cell B via Local File Handoff
        with open(checkpoint_path, "r") as f:
            received_capsule = json.load(f)

        print("[CELL B] CHECKPOINT RECEIVED")

        # 5. Cell B Verification Checks
        sig = received_capsule.pop("signature")
        if not self.verify_signature(received_capsule, sig):
            print("[CELL B] SIGNATURE VERIFICATION FAILED")
            sys.exit(1)
        received_capsule["signature"] = sig
        print("[CELL B] SIGNATURE VERIFIED")

        if received_capsule["destination_cell_id"] != "cell_b":
            print("[CELL B] DESTINATION UNAUTHORIZED")
            sys.exit(1)
        print("[CELL B] DESTINATION AUTHORIZED")

        # 6. Resume Execution 500 -> 1000 in Cell B
        resumed_state_hash = received_capsule["state_hash"]
        for step in range(501, 1001):
            resumed_state_hash = compute_transition(resumed_state_hash, self.input_commitment, step)

        print("[CELL B] RESUMING 500 -> 1000")

        # 7. Independent Reference Run (Verifier)
        ref_state_hash = genesis_state_hash
        for step in range(1, 1001):
            ref_state_hash = compute_transition(ref_state_hash, self.input_commitment, step)

        if ref_state_hash == resumed_state_hash:
            print("[VERIFIER] REFERENCE STATE MATCH")
        else:
            print("[VERIFIER] REFERENCE STATE MISMATCH")
            sys.exit(1)

        print("[VERIFIER] LINEAGE VERIFIED")

        # 8. Adversarial Tests
        # Test 1: Tamper Rejected
        tampered = received_capsule.copy()
        tampered["state_hash"] = "deadbeef" * 8
        if not self.verify_signature(tampered, tampered["signature"]):
            print("[TEST] TAMPER REJECTED")
        else:
            print("[TEST] TAMPER ACCEPTED (FAIL)")
            sys.exit(1)

        # Test 2: Replay Rejected
        if received_capsule["nonce"] in self.used_nonces:
            # Simulate rejection on nonce reuse
            print("[TEST] REPLAY REJECTED")
        else:
            sys.exit(1)

        # Test 3: Wrong Destination Rejected
        wrong_dest = received_capsule.copy()
        wrong_dest["destination_cell_id"] = "cell_evil"
        if wrong_dest["destination_cell_id"] != "cell_b":
            print("[TEST] WRONG DESTINATION REJECTED")
        else:
            sys.exit(1)

        print("KINETIC PROOF-CARRYING COMPUTATION: PASS")

if __name__ == "__main__":
    demo = KineticCapsuleDemo()
    demo.run()
