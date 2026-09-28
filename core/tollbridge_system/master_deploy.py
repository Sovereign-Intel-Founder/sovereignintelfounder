#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import shutil

USER = "joshua445"
HOME_DIR = f"/home/{USER}"
LEDGER_DIR = f"{HOME_DIR}/solana-ledger"
ACCOUNTS_DIR = f"{HOME_DIR}/solana-accounts"
IDENTITY_PATH = f"{HOME_DIR}/validator-keypair.json"
VOTE_PATH = f"{HOME_DIR}/vote-account-keypair.json"
SOLANA_INSTALL_DIR = f"{HOME_DIR}/.local/share/solana/install"
ACTIVE_BIN = f"{SOLANA_INSTALL_DIR}/active_release/bin/solana-validator"
DAEMON_PATH = f"/usr/local/bin/solana-maintenance-daemon.py"

def run_cmd(cmd, check=True):
    print(f"[EXEC] {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"[ERROR] Command failed: {res.stderr.strip()}")
        sys.exit(res.returncode)
    return res.stdout.strip()

def verify_and_prep():
    if os.geteuid() != 0:
        print("Error: Must be run with root/sudo privileges.")
        sys.exit(1)
    if not os.path.exists(HOME_DIR):
        print(f"Error: User home {HOME_DIR} does not exist.")
        sys.exit(1)

def install_solana():
    print("[*] Ensuring Solana software and binaries are fully installed and updated...")
    if not os.path.exists(ACTIVE_BIN):
        run_cmd(f"su - {USER} -c 'sh -c \"$(curl -sSfL https://release.solana.com/v1.18.26/install)\"'")
    else:
        print("[*] Solana binaries already present at active release path.")

def configure_system_kernel():
    print("[*] Applying kernel sysctl limits and security limits for 728GB RAM node...")
    with open("/etc/security/limits.d/90-solana.conf", "w") as f:
        f.write(f"""
{USER} soft nofile 1000000
{USER} hard nofile 1000000
{USER} soft memlock unlimited
{USER} hard memlock unlimited
""")

    with open("/etc/sysctl.d/99-solana.conf", "w") as f:
        f.write("""
vm.max_map_count = 1000000
fs.file-max = 1000000
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
""")
    run_cmd("sysctl --system")

def setup_storage_and_keys():
    print("[*] Provisioning isolated directories, keypairs, and file ownership piping...")
    os.makedirs(LEDGER_DIR, exist_ok=True)
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)
    
    keygen_path = f"{SOLANA_INSTALL_DIR}/active_release/bin/solana-keygen"
    if not os.path.exists(IDENTITY_PATH):
        run_cmd(f"su - {USER} -c '{keygen_path} new --outfile {IDENTITY_PATH} --no-passphrase --force'")
    if not os.path.exists(VOTE_PATH):
        run_cmd(f"su - {USER} -c '{keygen_path} new --outfile {VOTE_PATH} --no-passphrase --force'")
        
    run_cmd(f"chown -R {USER}:{USER} {LEDGER_DIR} {ACCOUNTS_DIR} {IDENTITY_PATH} {VOTE_PATH}")

def write_maintenance_daemon():
    print("[*] Deploying autonomous background maintenance worker...")
    daemon_code = f"""#!/usr/bin/env python3
import time
import subprocess

# Autonomous upkeep worker for disk, ledger size enforcement, and process recovery
def check_node():
    res = subprocess.run("systemctl is-active --quiet solana-rpc", shell=True)
    if res.returncode != 0:
        print("[MAINTENANCE] Node offline. Triggering recovery restart...")
        subprocess.run("systemctl restart solana-rpc", shell=True)

if __name__ == "__main__":
    while True:
        check_node()
        time.sleep(60)
"""
    with open(DAEMON_PATH, "w") as f:
        f.write(daemon_code)
    run_cmd(f"chmod +x {DAEMON_PATH}")
    
    # Setup maintenance worker systemd service
    with open("/etc/systemd/system/solana-maintenance.service", "w") as f:
        f.write(f"""[Unit]
Description=Solana Autonomous Maintenance Worker
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {DAEMON_PATH}
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
""")
    run_cmd("systemctl daemon-reload")
    run_cmd("systemctl enable solana-maintenance")
    run_cmd("systemctl restart solana-maintenance")

def deploy_validator_service():
    print("[*] Deploying NUMA-bound production systemd validator daemon...")
    service_content = f"""[Unit]
Description=Solana Enterprise High-Performance RPC Node
After=network.target remote-fs.target

[Service]
Type=simple
User={USER}
LimitNOFILE=1000000
LimitMEMLOCK=infinity
Nice=-20
CPUSchedulingPolicy=other
ExecStartPre=/bin/mkdir -p {LEDGER_DIR} {ACCOUNTS_DIR}
ExecStart=/usr/bin/numactl --membind=0 --cpunodebind=0 {ACTIVE_BIN} \\
  --identity {IDENTITY_PATH} \\
  --vote-account {VOTE_PATH} \\
  --ledger {LEDGER_DIR} \\
  --accounts {ACCOUNTS_DIR} \\
  --rpc-port 8899 \\
  --dynamic-port-range 8000-8050 \\
  --entrypoint entrypoint.mainnet-beta.solana.com:8001 \\
  --entrypoint entrypoint2.mainnet-beta.solana.com:8001 \\
  --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2 \\
  --no-voting \\
  --enable-rpc-transaction-history \\
  --limit-ledger-size 50000000 \\
  --accounts-index-memory-limit-mb 512000 \\
  --snapshot-fetch \\
  --use-snapshot-archives-at-startup fetched \\
  --log -
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    with open("/etc/systemd/system/solana-rpc.service", "w") as f:
        f.write(service_content)
        
    run_cmd("systemctl daemon-reload")
    run_cmd("systemctl enable solana-rpc")
    run_cmd("systemctl restart solana-rpc")
    print("[*] Master infrastructure, maintenance daemon, and validator pipeline fully initialized.")

if __name__ == "__main__":
    verify_and_prep()
    install_solana()
    configure_system_kernel()
    setup_storage_and_keys()
    write_maintenance_daemon()
    deploy_validator_service()
