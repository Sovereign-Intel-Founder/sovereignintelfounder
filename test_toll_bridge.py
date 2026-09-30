import asyncio
import json
from sip_remote_handoff.node_auth import SipHandoffNode

async def test_bridge():
    node = SipHandoffNode()
    
    payload = {"task": "benchmark_run", "lanes": 128}
    envelope = node.create_envelope(payload)
    
    reader, writer = await asyncio.open_connection('127.0.0.1', 8080)
    
    body = json.dumps(envelope).encode('utf-8')
    
    headers = [
        b"POST / HTTP/1.1",
        b"Host: 127.0.0.1:8080",
        b"X-Client-Hex: TEST_CLIENT_NODE",
        f"X-Node-Id: {envelope['node_id']}".encode('utf-8'),
        f"X-Signature: {envelope['signature']}".encode('utf-8'),
        f"Content-Length: {len(body)}".encode('utf-8'),
        b"Connection: close",
        b"",
        b""
    ]
    request = b"\r\n".join(headers) + body
    
    writer.write(request)
    await writer.drain()
    
    response = await reader.read(1024)
    print("--- BRIDGE RESPONSE ---")
    print(response.decode(errors="ignore"))
    writer.close()
    await writer.wait_closed()

asyncio.run(test_bridge())
