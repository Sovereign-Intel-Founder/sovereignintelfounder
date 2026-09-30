import struct

MAX_FRAME_SIZE = 1 * 1024 * 1024  # 1 MiB

def send_frame(sock, data: bytes):
    if len(data) == 0 or len(data) > MAX_FRAME_SIZE:
        raise ValueError(f"Invalid frame size: {len(data)}")
    header = struct.pack('>I', len(data))
    sock.sendall(header + data)

def recv_frame(sock) -> bytes:
    header = sock.recv(4)
    if not header or len(header) < 4:
        raise ConnectionError("Connection closed or truncated header")
    length = struct.unpack('>I', header)[0]
    if length == 0 or length > MAX_FRAME_SIZE:
        raise ValueError(f"Frame length {length} violates 1 MiB bounds or is zero")
    
    data = bytearray()
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Truncated frame payload")
        data.extend(chunk)
    return bytes(data)
