import urllib.request
import json

# Use local loopback for internal testing, public IP for external bots
NODE_ENDPOINT = "http://127.0.0.1:9999/process"

def execute_remote_task(task_name: str, payload_data: dict) -> dict:
    payload = json.dumps({"task": task_name, "data": payload_data}).encode('utf-8')
    req = urllib.request.Request(
        NODE_ENDPOINT,
        data=payload,
        headers={"User-Agent": "SovereignAgent-Framework/1.0", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

if __name__ == "__main__":
    print("Testing Ashburn accelerator hook...")
    result = execute_remote_task("bootstrap_sync", {"units": 128})
    print("Response:", result)
