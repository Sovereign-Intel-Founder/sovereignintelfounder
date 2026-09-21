#!/usr/bin/env python3
import os
import sys
import subprocess

USER = "joshua445"
HOME_DIR = f"/home/{USER}"
LEDGER_DIR = f"{HOME_DIR}/solana-ledger"
ACCOUNTS_DIR = f"{HOME_DIR}/solana-accounts"
IDENTITY_PATH = f"{HOME_DIR}/validator-keypair.json"
VOTE_PATH = f"{HOME_DIR}/vote-account-keypair.json"
SOLANA_INSTALL_DIR = f"{HOME_DIR}/.local/share/solana/install"
ACTIVE_BIN = f"{SOLANA_INSTALL_DIR}/active_release/bin/solana-validator"
KEYGEN_BIN = f"{SOLANA_INSTALL_DIR}/active_release/bin/solana-keygen"

def run_cmd(cmd, check=True):
    print(f"[EXEC] {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=HOME_DIR)
    if check and res.returncode != 0:
        print(f"[ERROR] Command failed: {res.stderr.strip()}")
        sys.exit(res.returncode)
    return res.stdout.strip()

if os.geteuid() != 0:
    print("Error: Must be run with sudo.")
    sys.exit(1)

os.chdir(HOME_DIR)

print("[*] Verifying and installing Solana binaries...")
if not os.path.exists(ACTIVE_BIN):
    run_cmd(f"sudo -u {USER} env HOME={HOME_DIR} bash -c 'sh -sSfL https://release.solana.com/v1.18.26/install' < /dev/null || true")

if not os.path.exists(ACTIVE_BIN):
    print("[ERROR] Solana binary path missing.")
    sys.exit(1)

print("[*] Applying kernel and security limits...")
with open("/etc/security/limits.d/90-solana.conf", "w") as f:
    f.write(f"{USER} soft nofile 1000000\n{USER} hard nofile 1000000\n{USER} soft memlock unlimited\n{USER} hard memlock unlimited\n")

with open("/etc/sysctl.d/99-solana.conf", "w") as f:
    f.write("vm.max_map_count = 1000000\nfs.file-max = 1000000\nnet.core.rmem_max = 134217728\nnet.core.wmem_max = 134217728\n")
run_cmd("sysctl --system")

print("[*] Setting up directories and keys...")
os.makedirs(LEDGER_DIR, exist_ok=True)
os.makedirs(ACCOUNTS_DIR, exist_ok=True)

if not os.path.exists(IDENTITY_PATH):
    run_cmd(f"sudo -u {USER} env HOME={HOME_DIR} {KEYGEN_BIN} new --outfile {IDENTITY_PATH} --no-passphrase --force")
if not os.path.exists(VOTE_PATH):
    run_cmd(f"sudo -u {USER} env HOME={HOME_DIR} {KEYGEN_BIN} new --outfile {VOTE_PATH} --no-passphrase --force")

run_cmd(f"chown -R {USER}:{USER} {LEDGER_DIR} {ACCOUNTS_DIR} {IDENTITY_PATH} {VOTE_PATH}")

print("[*] Deploying systemd service...")
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
WorkingDirectory={HOME_DIR}
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
print("[*] Deployment complete.")
