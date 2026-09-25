import urllib.request
import json
import concurrent.futures
import random

url = "http://127.0.0.1:9999/process"
agents = [
    "AutoScraper-Agent/3.2",
    "SovereignCrawler/1.0",
    "DataHarvester-Bot",
    "OpenAI-AgentRunner",
    "CustomNodeSync/v2"
]

def hit_node(i):
    agent = random.choice(agents)
    payload = json.dumps({"task": f"benchmark_compute_{i}", "compute_units": random.randint(1, 10)})
    req = urllib.request.Request(
        url,
        data=payload.encode('utf-8'),
        headers={"User-Agent": agent, "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Status: {resp.status} | Agent: {agent}")
    except Exception as e:
        print(f"Error: {e}")

print("🚀 Launching simulated bot swarm against local node...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(hit_node, range(25)))

print("Swarm simulation complete!")
