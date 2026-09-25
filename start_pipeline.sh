#!/bin/bash
echo "[*] Cleaning up existing instances..."
sudo pkill -f sovereign_live_engine
pkill -f live_feeder.py
sudo rm -f /dev/shm/sovereign_live_ring
rm -f engine.log feeder.log

# Ensure sys/stat.h is included for clean fchmod compilation
if ! grep -q "sys/stat.h" 02-low-latency/bitstream/tests/test_live_engine.c; then
    sed -i '/#include <sys\/mman.h>/a #include <sys/stat.h>' 02-low-latency/bitstream/tests/test_live_engine.c
fi

echo "[*] Compiling C consumer engine..."
gcc -O3 -march=native -mavx512f -mavx512cd -std=gnu11 -pthread \
    02-low-latency/bitstream/tests/test_live_engine.c \
    02-low-latency/toll_bridge/src/sovereign_toll_bridge.c \
    02-low-latency/mesh_index/src/sovereign_mesh_index.c \
    -I 02-low-latency/bitstream/include \
    -I 02-low-latency/bitstream/tests \
    -I 02-low-latency/toll_bridge/include \
    -I 02-low-latency/mesh_index/include \
    -lnuma \
    -o sovereign_live_engine

echo "[*] Launching C Consumer Engine..."
sudo ./sovereign_live_engine > engine.log 2>&1 &

echo "[*] Waiting for shared ring buffer..."
while [ ! -e /dev/shm/sovereign_live_ring ]; do
    sleep 0.1
done

echo "[*] Launching Python Live Feeder..."
python3 -u live_feeder.py > feeder.log 2>&1 &

echo "[*] Pipeline active! Opening live telemetry stream..."
sleep 1
tail -f engine.log feeder.log
