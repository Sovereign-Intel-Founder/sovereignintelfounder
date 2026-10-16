import socket
import struct

payload = struct.pack("<HHQI", 0x0001, 1, 0xDEADBEEF00000000, 0x12345678)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(payload, ("10.0.0.1", 9999))
print("Custom instruction packet sent!")
