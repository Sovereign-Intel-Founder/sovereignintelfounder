import mmap
import os
import struct
import time

SHM_NAME = "/dev/shm/sip_afxdp_ring"

def write_telemetry():
    # Pack 4 unsigned 64-bit integers: rx_packets, rx_bytes, valid_sigs, invalid_sigs
    data = struct.pack("QQQQ", 150000, 31457280, 75000, 75000)
    
    with open(SHM_NAME, "w+b") as f:
        f.write(b'\x00' * 48)
        f.flush()
        
    with open(SHM_NAME, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 48)
        mm[:32] = data
        mm.flush()
        mm.close()
    print("[✔] AF_XDP SHM Telemetry Ring populated successfully.")

if __name__ == '__main__':
    write_telemetry()
