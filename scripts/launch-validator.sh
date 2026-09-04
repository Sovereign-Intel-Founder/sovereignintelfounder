#!/bin/bash
set -e

echo "[+] Optimizing kernel parameters for high-spec node..."
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728
sudo sysctl -w vm.max_map_count=1000000
ulimit -n 1000000

echo "[+] Cleaning stale ledger lock files..."
rm -rf /home/joshua445/validator-ledger/*.lock

echo "[+] Stopping any lingering validator instances..."
sudo pkill -9 -f solana-validator || true

echo "[+] Launching Agave validator..."
exec /home/joshua445/.local/share/solana/install/active_release/bin/solana-validator \
    --identity /home/joshua445/validator-keypair.json \
    --ledger /home/joshua445/validator-ledger \
    --rpc-port 8899 \
    --gossip-port 8001 \
    --dynamic-port-range 8002-8051 \
    --entrypoint entrypoint.mainnet-beta.solana.com:8001 \
    --no-voting \
    --full-rpc-api \
    --rpc-pubsub-enable-block-subscription \
    --geyser-plugin-config /home/joshua445/geyser-plugin-config.json \
    --public-rpc-address 216.22.11.194:8899 \
    --no-xdp
