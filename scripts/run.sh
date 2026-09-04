#!/bin/bash
pkill -9 -f solana-validator || true
/home/joshua445/.local/share/solana/install/active_release/bin/solana-validator \
    --identity /home/joshua445/validator-keypair.json \
    --ledger /home/joshua445/validator-ledger \
    --rpc-port 8899 --gossip-port 8001 \
    --dynamic-port-range 8002-8051 \
    --entrypoint entrypoint.mainnet-beta.solana.com:8001 \
    --no-voting --full-rpc-api --enable-rpc-transaction-history \
    --geyser-plugin-config /home/joshua445/geyser-plugin-config.json \
    --public-rpc-address 216.22.11.194:8899 --no-xdp
