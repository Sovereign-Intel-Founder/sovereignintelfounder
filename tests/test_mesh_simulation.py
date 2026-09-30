import time
import os
from sip_remote_handoff.node_auth import SipHandoffNode
from sip_remote_handoff.pipeline_gate import ExecutionPipelineGate

def test_multi_node_mesh_handoff():
    # Spin up two distinct autonomous nodes with separate keypairs
    node_alpha = SipHandoffNode(key_path="alpha_node_key.bin")
    node_beta = SipHandoffNode(key_path="beta_node_key.bin")
    
    beta_gate = ExecutionPipelineGate(node_beta)

    # Node Alpha creates and signs a payload for the mesh
    envelope = node_alpha.create_envelope({"source": "alpha", "target": "beta", "data": "sync_packet"})

    # Node Beta's pipeline gate should successfully ingest Alpha's message
    assert beta_gate.ingest(envelope) == True, "Node Beta rejected valid message from Node Alpha!"

    # Cleanup simulation keys
    for path in ["alpha_node_key.bin", "beta_node_key.bin"]:
        if os.path.exists(path):
            os.remove(path)
    print("Multi-node handoff simulation passed cleanly.")

def test_pipeline_latency_microbenchmark():
    node = SipHandoffNode(key_path="bench_node_key.bin")
    gate = ExecutionPipelineGate(node)
    envelope = node.create_envelope({"benchmark": "ingress_speed", "value": 1})

    # Benchmark 10,000 ingest verifications to measure microsecond overhead
    iterations = 10000
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        assert gate.ingest(envelope) == True

    elapsed = time.perf_counter() - start_time
    avg_latency_us = (elapsed / iterations) * 1_000_000

    print(f"Benchmark: {iterations} verifications completed in {elapsed:.4f}s")
    print(f"Average Ingress Latency: {avg_latency_us:.2f} microseconds per check.")

    # Assert that overhead stays negligible (under 500 microseconds per verification)
    assert avg_latency_us < 500, f"Crypto verification latency too high: {avg_latency_us:.2f}µs"

    if os.path.exists("bench_node_key.bin"):
        os.remove("bench_node_key.bin")
    print("Latency microbenchmark passed cleanly.")
