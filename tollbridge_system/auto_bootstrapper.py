import time
import socket
import threading
import logging
import urllib.request
import json

logger = logging.getLogger("auto_bootstrapper")

class MasterNodeBootstrapper:
    def __init__(self, master_url: str = "http://127.0.0.1:8001/v1/cluster/register"):
        self.master_url = master_url
        self.node_id = f"node_{socket.gethostname()}_{int(time.time())}"
        self.is_registered = False

    def get_system_specs(self):
        return {
            "node_id": self.node_id,
            "address": socket.gethostbyname(socket.gethostname()),
            "cores": 128,  # Maps to your bare-metal config baseline
            "ram_gb": 728,
            "status": "active"
        }

    def register_with_master(self):
        payload = json.dumps(self.get_system_specs()).encode("utf-8")
        req = urllib.request.Request(
            self.master_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        
        while not self.is_registered:
            try:
                with urllib.request.urlopen(req, timeout=3) as response:
                    if response.status == 200:
                        self.is_registered = True
                        logger.info(f"Successfully auto-joined master cluster! Node ID: {self.node_id}")
                        return True
            except Exception as e:
                logger.warning(f"Master controller unreachable. Retrying auto-join handshake in 5s...")
                time.sleep(5)

    def start_background_handshake(self):
        t = threading.Thread(target=self.register_with_master, daemon=True)
        t.start()
