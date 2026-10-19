import os
import struct
import time
import mmap

SHM_NAME = "/sip_shm_channel"
SHM_SIZE = 4096

def query_sip_bridge(seed_value: int):
    shm_path = f"/dev/shm{SHM_NAME}"
    shm_fd = os.open(shm_path, os.O_RDWR)
    with mmap.mmap(shm_fd, SHM_SIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE) as mm:
        mm[16:20] = struct.pack("I", 0)
        mm[0:8] = struct.pack("Q", seed_value)
        mm[16:20] = struct.pack("I", 1)
        
        while True:
            status = struct.unpack("I", mm[16:20])[0]
            if status == 2:
                break
            time.sleep(0.0001)
            
        token = struct.unpack("Q", mm[8:16])[0]
        return token

if __name__ == "__main__":
    test_seed = 1337999111
    print(f"[*] Dispatching seed {test_seed} via POSIX shared memory...")
    result = query_sip_bridge(test_seed)
    print(f"[+] Received Secure Token Result: {result:016X}")
