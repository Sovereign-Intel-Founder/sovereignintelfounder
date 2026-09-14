import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
#!/usr/bin/env python3
"""
=========================================================================================
TOLL BRIDGE ENTERPRISE GATEWAY WORKER (bridge.py)
High-Performance Multi-Crypto Stream Receiver & Socket Forwarder.
Optimized with SO_REUSEADDR to prevent port bind collisions on restart.
=========================================================================================
"""

import socket
import sys
import logging
import time

HOST = '0.0.0.0'
PORT = 8080

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [BRIDGE-WORKER] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("BridgeWorker")

def main():
    logger.info(f"Initializing Bridge Worker socket on {HOST}:{PORT}...")
    
    # Create socket with socket reuse option to avoid [Errno 98] Address already in use
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind((HOST, PORT))
        s.listen(128)
        logger.info(f"Bridge Worker successfully bound to port {PORT}. Listening for multi-crypto traffic streams...")
        
        while True:
            conn, addr = s.accept()
            try:
                data = conn.recv(1024)
                if data:
                    logger.debug(f"Received stream payload from {addr}")
                    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
            except Exception as stream_err:
                logger.error(f"Stream error with {addr}: {stream_err}")
            finally:
                conn.close()
                
    except Exception as e:
        logger.error(f"Bridge socket binding failed: {e}")
        sys.exit(1)
    finally:
        s.close()

if __name__ == "__main__":
    main()
