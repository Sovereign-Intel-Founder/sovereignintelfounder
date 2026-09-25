import os
import mmap
import time
import json
import websocket
import ctypes

class LiveFrame(ctypes.Structure):
    _fields_ = [
        ("sequence_id", ctypes.c_uint64),
        ("capture_tsc", ctypes.c_uint64),
        ("flags", ctypes.c_uint8),
        ("payload_length", ctypes.c_uint32),
        ("payload", ctypes.c_uint8 * 239)
    ]

class SharedRing(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.c_uint64),
        ("tail", ctypes.c_uint64),
        ("frames", LiveFrame * 100000)
    ]

SHM_PATH = "/dev/shm/sovereign_live_ring"

print(f"[*] Connecting ctypes shared memory bridge at {SHM_PATH}...")
while not os.path.exists(SHM_PATH):
    time.sleep(0.1)

shm_fd = os.open(SHM_PATH, os.O_RDWR)
shm_mem = mmap.mmap(shm_fd, ctypes.sizeof(SharedRing), mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
ring = SharedRing.from_buffer(shm_mem)

sequence_id = 0

def run_live_feed():
    global sequence_id
    ws_url = "wss://api.mainnet-beta.solana.com"
    sub_payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "slotSubscribe"
    })

    def on_message(ws, message):
        global sequence_id
        try:
            data = json.loads(message)
            slot = data.get("params", {}).get("result", {}).get("slot", 0)
            
            if slot > 0:
                tail = ring.tail
                head = ring.head
                
                # Backpressure protection: skip or block gracefully if ring is saturated
                if tail - head < 99000:
                    idx = tail % 100000
                    frame = ring.frames[idx]
                    frame.sequence_id = sequence_id
                    frame.capture_tsc = time.time_ns()
                    frame.flags = 0xA5  
                    frame.payload_length = 239
                    
                    slot_bytes = str(slot).encode('utf-8')
                    payload_arr = (ctypes.c_uint8 * 239)()
                    for i in range(min(len(slot_bytes), 239)):
                        payload_arr[i] = slot_bytes[i]
                    frame.payload = payload_arr
                    
                    ring.tail = tail + 1
                    sequence_id += 1
        except Exception:
            pass

    def on_open(ws):
        print(f"[*] Connected to Live Mainnet Wire: {ws_url}. Subscribing...")
        ws.send(sub_payload)

    def on_error(ws, error):
        print(f"[-] WebSocket Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"[-] WebSocket Disconnected ({close_status_code}: {close_msg}). Reconnecting in 1s...")

    # Infinite Watchdog Reconnect Loop
    while True:
        try:
            ws = websocket.WebSocketApp(ws_url,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            print(f"[-] Reconnect loop exception: {e}")
        time.sleep(1.0)

if __name__ == "__main__":
    run_live_feed()
