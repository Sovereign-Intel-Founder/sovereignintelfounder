import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:8080/v1/ingress"
print("[*] Probing Ingress Route with Empty Payload...")

try:
    req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Body: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"[!] HTTP Error Encountered: {e.code} - {e.reason}")
    print(f"Response body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"[!] Connection Error: {e}")

