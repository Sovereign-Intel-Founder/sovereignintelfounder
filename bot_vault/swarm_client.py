import concurrent.futures
import urllib.request
import json
import random

URL = "http://localhost:9999/process"
USER_AGENTS = [
    "AgentSwarm-Alpha/1.0",
    "LangChainAgent/2.4",
    "AutonomousScraper-X/9.1",
    "OpenAI-DataCrawler/3.0",
    "MCP-ToolRunner/0.5",
    "SovereignNode-Agent/1.2"
]

def send_request(i):
    ua = random.choice(USER_AGENTS)
    payload = json.dumps({"task": f"synthetic_workload_{i}", "compute_units": random.randint(10, 100)})
    req = urllib.request.Request(
        URL,
        data=payload.encode('utf-8'),
        headers={
            "User-Agent": ua,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status
    except Exception as e:
        return str(e)

def main():
    print("🚀 Launching 100-request multi-threaded bot swarm against Ashburn node...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(send_request, i) for i in range(100)]
        results = [f.result() for f in futures]
    print(f"✅ Dispatched {len(results)} synthetic bot requests successfully.")

if __name__ == "__main__":
    main()
