from sip_remote_handoff.node_auth import SipHandoffNode

def main():
    node = SipHandoffNode()
    print(f"Node initialized: {node.node_id}")

if __name__ == "__main__":
    main()
