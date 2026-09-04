ls -lh /mnt/snapshots
solana-snapshot-finder --snapshot-dir /mnt/snapshots
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
sudo mkdir -p /mnt/snapshots
cd /mnt/snapshots
sudo wget $(curl -s https://api.mainnet-beta.solana.com -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"getHighestSnapshotSlot"}' | jq -r '"https://api.mainnet-beta.solana.com/snapshot.tar.bz2"')
docker run --rm -v /mnt/snapshots:/snapshots ghcr.io/21st-dev/solana-snapshot-finder:latest --snapshot-dir /snapshots
sudo docker run --rm   -v /mnt/snapshots:/snapshot   c29r3/solana-snapshot-finder:latest   --snapshot_path /snapshot
sudo docker pull c29r3/solana-snapshot-finder:latest
sudo docker run -it --rm   -v /mnt/snapshots:/solana/snapshot   --user $(id -u):$(id -g)   c29r3/solana-snapshot-finder:latest   --snapshot_path /solana/snapshot
sudo wget -O /mnt/snapshots/snapshot.tar.bz2 https://api.mainnet-beta.solana.com/snapshot.tar.bz2
sudo chown -R $USER:$USER /mnt/snapshots
docker run --rm -v /mnt/snapshots:/snapshot ghcr.io/21st-dev/solana-snapshot-finder:latest --snapshot-dir /snapshot
sudo docker run --rm -v /mnt/snapshots:/snapshot ghcr.io/21st-dev/solana-snapshot-finder:latest --snapshot-dir /snapshot
sudo docker run --rm -v /mnt/snapshots:/snapshot c29r3/solana-snapshot-finder:latest --snapshot_path /snapshot
sudo docker run --rm -v /mnt/snapshots:/snapshot c29r3/solana-snapshot-finder:latest --snapshot_path /snapshot
sudo chmod 777 /mnt/snapshots
sudo docker run --rm -v /mnt/snapshots:/snapshot c29r3/solana-snapshot-finder:latest --snapshot_path /snapshot
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
sudo rm -f /mnt/snapshots/*.tar.* /mnt/snapshots/*.zst /mnt/snapshots/*.bz2
sudo rm -rf /mnt/ramdisk/ledger/* /mnt/ramdisk/accounts/*
df -h
sudo apt-get clean
sudo apt-get autoremove -y
sudo journalctl --vacuum-time=1d
sudo rm -rf ~/.cache/*
sudo mkdir -p /mnt/ramdisk/snapshots
sudo rm -rf /mnt/snapshots/*
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
sudo chmod 777 /mnt/ramdisk/snapshots
[200~agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check \
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
ps aux | grep validator
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
sudo fuser -k 8001/udp
sudo fuser -k 8001/tcp
pkill -9 agave-validator
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
sudo ss -lupn 'sport = :8001 or dport = :8001'
sudo netstat -tulpn | grep 8001
ps aux | grep -iE 'solana|agave'
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --gossip-bind-address 0.0.0.0   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
ip a
sudo ufw enable
sudo ufw allow 8001/udp
sudo ufw allow 8001/tcp
sudo ufw allow 8002:8051/udp
sudo ufw allow 8002:8051/tcp
sudo ufw reload
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --entrypoint entrypoint2.mainnet-beta.solana.com:8001   --entrypoint entrypoint3.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
sudo netstat -s | grep -i "drop\|failed"
ip route show
sudo ip route replace default via 216.22.11.254 dev ens5f0np0 onlink
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --gossip-bind-address 0.0.0.0   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /mnt/ramdisk/ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
timedatectl status
sudo tcpdump -i ens5f0np0 udp port 8001 -nn
solana-gossip --entrypoint 216.22.11.194:8001 spy
solana-gossip spy --entrypoint 216.22.11.194:8001
solana-gossip spy --entrypoint entrypoint.mainnet-beta.solana.com:8001
solana-gossip spy --entrypoint 216.22.11.194:8001 --gossip-port 8099
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --known-validator De1zDNA4dLKQEPGTsDBzvNeV9d8dF6mK6wZJ5mY1vXz   --known-validator CakcnaRDHka2gXyfbEd1d3XWk59uB155xW94C8r2Qk1k   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --known-validator De1zDNA4dLKQEPGTsDBzvNeV9d8dF6mK6wZJ5mY1vXz   --known-validator CakcnaRDHka2gXyfbEd1d3XWk59uB155xW94C8r2Qk1k   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
ls -lh /mnt/ramdisk/snapshots
ls -lh /home/joshua445/validator-ledger
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
--no-voting   --only-known-rpc   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --no-voting   --only-known-rpc   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --snapshot-archive-path /home/joshua445/validator-ledger/snapshots/snapshot-44352501-8pWthcZrtFtallAszgFrPRzcy3w51PXn8aiqFiCA.tar.zst   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
ps aux | grep agave-validator
nohup /home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log /home/joshua445/validator-ledger/validator.log &
sudo ufw status
rm -f /home/joshua445/validator-ledger/lock
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --no-voting   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --no-voting   --limit-ledger-size 50000000   --no-port-check   --wal-recovery-mode skip_any   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --expected-bank-hash 8pWthcZrtFtallAszgFrPRzcy3w51PXn8aiqFiCA   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --no-voting   --limit-ledger-size 50000000   --no-port-check   --log -
ls -la /home/joshua445/validator-ledger/snapshots
ls -la /home/joshua445/validator-ledger/snapshots/443569505
mv /home/joshua445/validator-ledger/snapshots/443569505/443569505 /home/joshua445/validator-ledger/snapshots/
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --no-voting   --limit-ledger-size 50000000   --no-port-check   --log -
sudo tcpdump -i any -nn 'udp portrange 8001-8051'
ip link show
nc -zv 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2 8899
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --no-voting   --no-port-check   --full-rpc-api   --limit-ledger-size 50000000   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --no-voting   --limit-ledger-size 50000000   --no-port-check   --log -
sudo nano /etc/systemd/system/agave-validator.service
sudo systemctl list-units --type=service | grep -i agave
sudo systemctl list-units --type=service | grep -i solana
sudo systemctl stop agave-validator.service solana-validator.service solana.service
sudo systemctl disable solana-validator.service solana.service
sudo pkill -9 agave-validator
sudo pkill -9 solana-validator
sudo rm -f /etc/systemd/system/solana-validator.service /etc/systemd/system/solana.service
sudo systemctl daemon-reload
sudo systemctl enable --now agave-validator.service
sudo journalctl -u agave-validator.service -f -n 100
which agave-validator
sudo cp /home/joshua445/.local/share/solana/install/active_release/bin/agave-validator /usr/local/bin/agave-validator
sudo nano /etc/systemd/system/agave-validator.service
git checkout -- init.toml
# or
git restore init.toml
sudo nano /etc/systemd/system/agave-validator.service
sudo systemctl daemon-reload
sudo systemctl restart agave-validator.service
sudo journalctl -u agave-validator.service -f -n 100
# 1. Copy the binary to a global path to bypass systemd sandbox restrictions
sudo cp /home/joshua445/.local/share/solana/install/active_release/bin/solana-validator /usr/local/bin/solana-validator
# 2. Write the clean systemd configuration directly
sudo tee /etc/systemd/system/agave-validator.service > /dev/null << 'EOF'
[Unit]
Description=Agave RPC Validator
After=network.target

[Service]
Type=simple
User=joshua445
LimitNOFILE=1000000
ExecStart=/usr/local/bin/solana-validator \
  --identity /home/joshua445/validator-keypair.json \
  --ledger /home/joshua445/validator-ledger \
  --snapshots /home/joshua445/validator-ledger/snapshots \
  --accounts /home/joshua445/validator-ledger/accounts \
  --use-snapshot-archives-at-startup \
  --rpc-port 8899 \
  --gossip-port 8001 \
  --dynamic-port-range 8002-8051 \
  --entrypoint entrypoint.mainnet-beta.solana.com:8001 \
  --entrypoint entrypoint2.mainnet-beta.solana.com:8001 \
  --expected-genesis-hash Seykt4USfV8P8NJdTREpY1vzqKqZKuKuc147dx2N9d \
  --known-validator 7Np41oeYqPPjNee3VBNWkRy12y8f4EgGj1XZ4X3D9MK1 \
  --known-validator GdnSyH3TwcXFqZvJMlJhtS4QVX7MFSx56uJLUfIZ \
  --only-known-rpc \
  --full-rpc-api \
  --no-voting \
  --enable-zpc-transaction-history \
  --limit-ledger-size 50000000 \
  --rpc-bind-address 0.0.0.0 \
  --no-xdp \
  --no-port-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 3. Reload systemd, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable --now agave-validator.service
# Copy the correct agave-validator binary globally
sudo cp /home/joshua445/.local/share/solana/install/active_release/bin/agave-validator /usr/local/bin/agave-validator
# Write the systemd service file using the correct binary name
sudo tee /etc/systemd/system/agave-validator.service > /dev/null << 'EOF'
[Unit]
Description=Agave RPC Validator
After=network.target

[Service]
Type=simple
User=joshua445
LimitNOFILE=1000000
ExecStart=/usr/local/bin/agave-validator \
  --identity /home/joshua445/validator-keypair.json \
  --ledger /home/joshua445/validator-ledger \
  --snapshots /home/joshua445/validator-ledger/snapshots \
  --accounts /home/joshua445/validator-ledger/accounts \
  --use-snapshot-archives-at-startup \
  --rpc-port 8899 \
  --gossip-port 8001 \
  --dynamic-port-range 8002-8051 \
  --entrypoint entrypoint.mainnet-beta.solana.com:8001 \
  --entrypoint entrypoint2.mainnet-beta.solana.com:8001 \
  --expected-genesis-hash Seykt4USfV8P8NJdTREpY1vzqKqZKuKuc147dx2N9d \
  --known-validator 7Np41oeYqPPjNee3VBNWkRy12y8f4EgGj1XZ4X3D9MK1 \
  --known-validator GdnSyH3TwcXFqZvJMlJhtS4QVX7MFSx56uJLUfIZ \
  --only-known-rpc \
  --full-rpc-api \
  --no-voting \
  --enable-zpc-transaction-history \
  --limit-ledger-size 50000000 \
  --rpc-bind-address 0.0.0.0 \
  --no-xdp \
  --no-port-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and start the service
sudo systemctl daemon-reload
sudo systemctl enable --now agave-validator.service
sudo journalctl -u agave-validator.service -f -n 50
sudo tee /etc/systemd/system/agave-validator.service > /dev/null << 'EOF'
[Unit]
Description=Agave RPC Validator
After=network.target

[Service]
Type=simple
User=joshua445
LimitNOFILE=1000000
ExecStart=/usr/local/bin/agave-validator \
  --identity /home/joshua445/validator-keypair.json \
  --ledger /home/joshua445/validator-ledger \
  --snapshots /home/joshua445/validator-ledger/snapshots \
  --accounts /home/joshua445/validator-ledger/accounts \
  --use-snapshot-archives-at-startup \
  --rpc-port 8899 \
  --gossip-port 8001 \
  --dynamic-port-range 8002-8051 \
  --entrypoint entrypoint.mainnet-beta.solana.com:8001 \
  --entrypoint entrypoint2.mainnet-beta.solana.com:8001 \
  --expected-genesis-hash Seykt4USfV8P8NJdTREpY1vzqKqZKuKuc147dx2N9d \
  --known-validator 7Np41oeYqPPjNee3VBNWkRy12y8f4EgGj1XZ4X3D9MK1 \
  --known-validator GdnSyH3TwcXFqZvJMlJhtS4QVX7MFSx56uJLUfIZ \
  --only-known-rpc \
  --full-rpc-api \
  --no-voting \
  --enable-rpc-transaction-history \
  --limit-ledger-size 50000000 \
  --rpc-bind-address 0.0.0.0 \
  --no-xdp \
  --no-port-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart agave-validator.service
sudo journalctl -u agave-validator.service -f -n 50
[Unit]
Description=Solana Agave Validator
After=network.target
[Service]
Type=simple
User=joshua445
Restart=always
RestartSec=10
LimitNOFILE=1000000
LimitMEMLOCK=infinity
ExecStart=/usr/local/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --rpc-port 8899   --gossip-port 8001   --dynamic-port-range 8002-8051   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --entrypoint entrypoint2.mainnet-beta.solana.com:8001   --expected-genesis-hash Seykt4USfV8P8NJdTREpY1vzqKqZKuKuc147dx2N9d   --known-validator 7Np41oeYqPPjNee3VBNWkRy12y8f4EgGj1XZ4X3D9MK1   --known-validator GdnSyH3TwcXFqZvJMlJhtS4QVX7MFSx56uJLUfIZ   --only-known-rpc   --full-rpc-api   --no-voting   --enable-rpc-transaction-history   --limit-ledger-size 50000000   --rpc-bind-address 0.0.0.0   --no-xdp   --no-port-check
[Install]
WantedBy=multi-user.target
exit
tail -f /home/joshua455/tollbridge_system/cluster_engine/bridge.log
bmon
tail -f /mnt/ledger/agave-validator.log | grep -E "JSON-RPC|slot|peering"
ps aux | grep cluster_engine
watch -n 0.5 "ps aux | grep cluster_engine_128core.py | grep -v grep"
V
ls -la /opt/bot_infrastructure/master_cluster/geyser_ingest/
cat /opt/bot_infrastructure/master_cluster/geyser_ingest/setup_demo.sh
cat /etc/systemd/system/geyser_ingest.service
sudo bash -c 'cat << 'EOF' > /etc/systemd/system/geyser_ingest.service
[Unit]
Description=Sovereign Intelligence Protocol Geyser Ingest Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bot_infrastructure/master_cluster/geyser_ingest
Environment="GEYSER_ENDPOINTS=http://127.0.0.1:10000,http://127.0.0.1:10001"
ExecStart=/opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF'
sudo systemctl daemon-reload
sudo systemctl restart geyser_ingest.service
sudo systemctl status geyser_ingest.service
grep -rn "env(" /opt/bot_infrastructure/master_cluster/geyser_ingest/src/
grep -rn "env(" /opt/bot_infrastructure/master_cluster/geyser_ingest/src/
sudo tee /etc/systemd/system/geyser_ingest.service > /dev/null << 'EOF'
[Unit]
Description=Sovereign Intelligence Protocol Geyser Ingest Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bot_infrastructure/master_cluster/geyser_ingest
EOF

sudo tee -a /etc/systemd/system/geyser_ingest.service > /dev/null << 'EOF'
Environment="GEYSER_ENDPOINTS=http://127.0.0.1:8899"
ExecStart=/opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart geyser_ingest.service
sudo systemctl status geyser_ingest.service
grep -rn "grpc" /opt/bot_infrastructure/master_cluster/ --exclude-dir=target
sudo ss -tulpn | grep LISTEN
sudo tee /etc/systemd/system/geyser_ingest.service > /dev/null << 'EOF'
[Unit]
Description=Sovereign Intelligence Protocol Geyser Ingest Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bot_infrastructure/master_cluster/geyser_ingest
EOF

sudo tee -a /etc/systemd/system/geyser_ingest.service > /dev/null << 'EOF'
Environment="GEYSER_ENDPOINTS=http://127.0.0.1:80"
ExecStart=/opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart geyser_ingest.service
sudo systemctl status geyser_ingest.service
sudo tee /etc/systemd/system/geyser_ingest.service > /dev/null << 'EOF'
[Unit]
Description=Sovereign Intelligence Protocol Geyser Ingest Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bot_infrastructure/master_cluster/geyser_ingest
EOF

sudo tee -a /etc/systemd/system/geyser_ingest.service > /dev/null << 'EOF'
Environment="GEYSER_ENDPOINTS=http://127.0.0.1:8899"
ExecStart=/opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart geyser_ingest.service
sudo systemctl status geyser_ingest.service
grep -rn "rpc_server_addr" /opt/bot_infrastructure/master_cluster/ --exclude-dir=target
grep -rn "rpc_server_addr" /opt/bot_infrastructure/master_cluster/ --exclude-dir=target
cat /opt/bot_infrastructure/master_cluster/geyser_ingest/setup_demo.sh
find /opt/bot_infrastructure/master_cluster/geyser_ingest -maxdepth 2 -type f
grep -rn "GEYSER" /opt/bot_infrastructure/master_cluster/geyser_ingest/src/main.rs
sed -n '110,135p' /opt/bot_infrastructure/master_cluster/geyser_ingest/src/main.rs
grep -rn "run_geyser_client" /opt/bot_infrastructure/master_cluster/geyser_ingest/src/
sed -n '31,65p' /opt/bot_infrastructure/master_cluster/geyser_ingest/src/main.rs
sudo ss -tlnp | grep -E '1000|889|geyser|validator|java|node'
sudo ss -tlnp
/opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
sudo /opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
find /opt/bot_infrastructure/master_cluster/ -maxdepth 2 -name "*.py" -o -name "*.sh"
python3 /opt/bot_infrastructure/master_cluster/ext_stream_gateway.py
GEYSER_ENDPOINTS="http://127.0.0.1:8888" /opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
sudo GEYSER_ENDPOINTS="http://127.0.0.1:8888" /opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
python3 /opt/bot_infrastructure/master_cluster/ext_stream_gateway.py &
sleep 2
sudo GEYSER_ENDPOINTS="http://127.0.0.1:8888" /opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
pkill -f ext_stream_gateway.py
python3 /opt/bot_infrastructure/master_cluster/stream_gateway_engine.py
pkill -f stream_gateway_engine.py
python3 -c "import http.server, socketserver; handler = http.server.SimpleHTTPRequestHandler; http.server.HTTPServer(('127.0.0.1', 8888), handler).serve_forever()" &
sudo GEYSER_ENDPOINTS="http://127.0.0.1:8888" /opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
pkill -f http.server
python3 /opt/bot_infrastructure/master_cluster/stream_gateway_engine.py &
sudo GEYSER_ENDPOINTS="http://127.0.0.1:8888" /opt/bot_infrastructure/master_cluster/geyser_ingest/target/release/ashburn_geyser_ingest
sudo netstat -tulpn | grep 8888
sudo netstat -tulpn | grep 8888
python3 /opt/bot_infrastructure/master_cluster/stream_gateway_engine.py
python3 /opt/bot_infrastructure/master_cluster/setup_demo.sh
head -n 30 /opt/bot_infrastructure/master_cluster/stream_gateway_engine.py
sed -n '30,70p' /opt/bot_infrastructure/master_cluster/ext_stream_gateway.py
tail -n 25 /opt/bot_infrastructure/master_cluster/ext_stream_gateway.py
find /opt/bot_infrastructure/master_cluster/geyser_ingest -name "*.toml" -o -name "*.json"
ls -la /opt/bot_infrastructure/master_cluster/
which solana-validator || find / -name "solana-validator" 2>/dev/null
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --dynamo-read-nodes 0
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-keygen new --no-passphrase -o ~/validator-keypair.json && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting
tail -n 20 /home/joshua445/agave-validator-*.log && ss -tulpn | grep 8899
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
sudo bash -c 'cat > /etc/sysctl.d/20-solana-validator.conf <<EOF
fs.file-max = 1000000
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.netdev_max_backlog = 16384
EOF' && sudo sysctl -p /etc/sysctl.d/20-solana-validator.conf
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp   --skip-startup-check os-network-limits
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rc   --no-voting   --no-xdp
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-genesis   --ledger ~/validator-ledger   --bootstrap-validator ~/validator-keypair.json   --cluster-type development   --hashes-per-tick sleep
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-genesis   --ledger ~/validator-ledger   --bootstrap-validator ~/validator-keypair.json   --cluster-type development   --hashes-per-tick sleep && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-genesis   --ledger ~/validator-ledger   --bootstrap-validator ~/validator-keypair.json   --cluster-type development   --hashes-per-tick sleep && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-genesis   --ledger ~/validator-ledger   --bootstrap-validator ~/validator-keypair.json   --cluster-type development   --hashes-per-tick sleep && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
ls -la /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana genesis   --ledger ~/validator-ledger   --bootstrap-validator ~/validator-keypair.json   --cluster-type development   --hashes-per-tick sleep && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --full-rpc-api   --private-rpc   --no-voting   --no-xdp
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1
tail -f ~/validator-ledger/validator.log
pkill -9 solana-test-validator solana-validator; rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8009   --tpu-port 8003
pkill -9 solana-test-validator solana-validator; rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8009   --tpu-port 8003
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8009
tail -f ~/validator-ledger/validator.log
sudo netstat -nlp | grep -E '8001|8009|8899'
sudo kill -9 2239207 && rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8009
sudo kill -9 2239207 && rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8009
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8015   --tpu-bundler-port 8017   --dynamic-port-range 8020-8040
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8015   --dynamic-port-range 8020-8040
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1   --gossip-port 8015   --dynamic-port-range 8020-8040
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --bind-address 127.0.0.1
tail -f ~/validator-ledger/validator.log
pkill -9 -f solana-test-validator && rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger
pkill -9 -f solana-test-validator && rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger
tail -f ~/validator-ledger/validator.log
pkill -9 -f solana && rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899
tail -f ~/validator-ledger/validator.log
pkill -9 -f solana && rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050
tail -f ~/validator-ledger/validator.log
df -h
rm -rf ~/validator-ledger && /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-test-validator   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --limit-ledger-size 50000000
rm -rf ~/validator-ledger && mkdir -p ~/validator-ledger
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uMLUfiZ   --no-voting   --full-rpc-api   --limit-ledger-size 50000000   --geyser-plugin-config ~/geyser-plugin-config.json
tail -n 50 ~/agave-validator-*.log
/home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uMLUfiZ   --no-voting   --full-rpc-api   --limit-ledger-size 50000000   --geyser-plugin-config ~/geyser-plugin-config.json   --no-xdp
SOLANA_METRICS_CONFIG="" /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uMLUfiZ   --no-voting   --full-rpc-api   --limit-ledger-size 50000000   --geyser-plugin-config ~/geyser-plugin-config.json   --bind-address 127.0.0.1
SOLANA_METRICS_CONFIG="" /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uMLUfiZ   --no-voting   --full-rpc-api   --limit-ledger-size 50000000   --geyser-plugin-config ~/geyser-plugin-config.json   --gossip-host 216.22.11.194   --public-rpc-address 216.22.11.194:8899
SOLANA_METRICS_CONFIG="" /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uMLUfiZ   --no-voting   --full-rpc-api   --limit-ledger-size 50000000   --geyser-plugin-config ~/geyser-plugin-config.json   --gossip-address 216.22.11.194:8900   --public-rpc-address 216.22.11.194:8899
SOLANA_METRICS_CONFIG="" /home/joshua445/.local/share/solana/install/releases/stable-75f9b5b4c3d8b24ae7200f0202bd08cbe29af2bc/solana-release/bin/solana-validator   --identity ~/validator-keypair.json   --ledger ~/validator-ledger   --rpc-port 8899   --gossip-port 8900   --dynamic-port-range 9000-9050   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uMLUfiZ   --no-voting   --full-rpc-api   --limit-ledger-size 50000000   --geyser-plugin-config ~/geyser-plugin-config.json   --public-rpc-address 216.22.11.194:8899
pkill -9 -f solana-validator || true
rm -rf /home/joshua445/validator-ledger/*
solana-validator     --identity /home/joshua445/validator-keypair.json     --ledger /home/joshua445/validator-ledger     --rpc-port 8899     --gossip-port 8001     --dynamic-port-range 8002-8051     --entrypoint entrypoint.mainnet-beta.solana.com:8001     --no-voting     --full-rpc-api     --enable-rpc-transaction-history     --geyser-plugin-config /home/joshua445/geyser-plugin-config.json     --trusted-validator 7Np41oeYqPpjNee3VBNWRky12y8f4EgGj1XZ4H3D9mK1
sudo nano /etc/systemd/system/agave-validator.service
sudo systemctl daemon-reload
rm -rf /home/joshua445/validator-ledger/*
sudo systemctl enable --now agave-validator
journalctl -u agave-validator -f
sudo nano /etc/systemd/system/agave-validator.service
sudo systemctl daemon-reload
rm -rf /home/joshua445/validator-ledger/*
sudo systemctl enable --now agave-validator
journalctl -u agave-validator -f
journalctl -u agave-validator -f
agave-validator --ledger ~/solana-ledger monitor
sudo journalctl -u agave-validator.service -n 20 --no-tail
agave-validator --ledger /home/joshua445/validator-ledger monitor
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator --ledger /home/joshua445/validator-ledger monitor
sudo grep -A 2 "\-\-ledger" /etc/systemd/system/agave-validator.service
/home/joshua445/.local/share/solana/install/active_release/bin/solana-validator --ledger /home/joshua445/validator-ledger monitor
htop
kill -15 $(pgrep agave-validator)
sudo systemctl disable agave-validator
sudo ss -lupn | grep 8001
sudo ss -lupn | grep 8001
agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /mnt/ramdisk/snapshots   --accounts /mnt/ramdisk/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
solana catchup --our-node ~/validator-keypair.json
--known-validator 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --known-validator De1zDNA4dLKQEPGTsDBzvNeV9d8dF6mK6wZJ5mY1vXz   --known-validator CakcnaRDHka2gXyfbEd1d3XWk59uB155xW94C8r2Qk1k   --expected-validators 7Np41oeYqPefeNQEHSv1UDhYrehxis3NStELsSKCT4K2
tail -f /home/joshua445/validator-ledger/validator.log
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
tail -f /home/joshua445/validator-ledger/validator.log
/home/joshua445/.local/share/solana/install/active_release/bin/agave-validator   --identity /home/joshua445/validator-keypair.json   --ledger /home/joshua445/validator-ledger   --snapshots /home/joshua445/validator-ledger/snapshots   --accounts /home/joshua445/validator-ledger/accounts   --use-snapshot-archives-at-startup   --entrypoint entrypoint.mainnet-beta.solana.com:8001   --known-validator GdnSyH3YtwcxFvQrVVJMm1JhTS4QVX7MFsX56uJLUfiZ   --rpc-port 8899   --rpc-bind-address 0.0.0.0   --gossip-host 216.22.11.194   --gossip-port 8001   --dynamic-port-range 8002-8051   --full-rpc-api   --limit-ledger-size 50000000   --no-port-check   --log -
tail -f /home/joshua445/validator-ledger/validator.log
rm -rf /home/joshua445/validator-ledger/snapshots/443568705 /home/joshua445/validator-ledger/snapshots/443569505
tail -f /mnt/ledger/agave-validator.log | grep -E "JSON-RPC|slot|peering|shred"
htop -d 10
