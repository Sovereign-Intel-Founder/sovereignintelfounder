import subprocess
import sys

cmd = [
    "qemu-system-x86_64",
    "-cpu", "max",
    "-smp", "4,cores=4,threads=1",
    "-m", "2G",
    "-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd",
    "-drive", "file=sovereign.img,format=raw",
    "-serial", "stdio",
    "-display", "none"
]

print("[*] Starting Sovereign Automated Test Harness...")
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

success = False
try:
    for line in process.stdout:
        print(line, end="")
        if "[SUCCESS]" in line:
            success = True
            process.terminate()
            break
except Exception as e:
    print(f"[-] Error reading stream: {e}")

process.wait()

if success:
    print("\n[+] TEST RUNNER: SUCCESS - All assertions verified.")
    sys.exit(0)
else:
    print("\n[-] TEST RUNNER: FAILED - Success marker not detected.")
    sys.exit(1)
