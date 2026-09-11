#!/bin/bash
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Directories setup
mkdir -p /home/joshua445/solana-ledger /home/joshua445/solana-accounts

exec solana-validator \
  --identity /home/joshua445/validator-keypair.json \
  --vote-account /home/joshua445/vote-account-keypair.json \
  --ledger /home/joshua445/solana-ledger \
  --accounts /home/joshua445/solana-accounts \
  --rpc-port 8899 \
  --dynamic-port-range 8000-8050 \
  --entrypoint entrypoint.mainnet-beta.solana.com:8001 \
  --entrypoint entrypoint2.mainnet-beta.solana.com:8001 \
  --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2 \
  --no-voting \
  --enable-rpc-transaction-history \
  --enable-rpc-historical-ledger \
  --limit-ledger-size 50000000 \
  --accounts-index-memory-limit-mb 512000 \
  --snapshot-fetch \
  --use-snapshot-archives-at-startup fetched \
  --log -
