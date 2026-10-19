import json, ipaddress
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class PeerConfig:
    peer_id: str
    endpoint_ip: str
    endpoint_port: int

@dataclass(frozen=True)
class NodeConfig:
    node_id: str
    listen_ip: str
    listen_port: int
    peers: List[PeerConfig]

def load_and_validate(path: str) -> NodeConfig:
    with open(path) as f:
        d = json.load(f)
    ipaddress.ip_address(d["listen_ip"])
    assert 1 <= int(d["listen_port"]) <= 65535, "Invalid port bounds"
    peers = []
    for p in d.get("peers", []):
        ip_str, port_str = p["endpoint"].rsplit(":", 1)
        ipaddress.ip_address(ip_str)
        assert 1 <= int(port_str) <= 65535, "Invalid peer port"
        peers.append(PeerConfig(p["peer_id"], ip_str, int(port_str)))
    return NodeConfig(d["node_id"], d["listen_ip"], int(d["listen_port"]), peers)
