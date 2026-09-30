import os
from sip_remote_handoff.node_auth import SipHandoffNode

def main():
    print("Initializing node key material...")
    node = SipHandoffNode()
    print(f"Node ID initialized successfully: {node.node_id}")

if __name__ == "__main__":
    main()
