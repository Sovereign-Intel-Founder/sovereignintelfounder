#!/usr/bin/env bash
set -euo pipefail

SESSION="sip_demo"

# Resolve Project Directory
if [ -d "/opt/bot_infrastructure/master_cluster" ]; then
    DIR="/opt/bot_infrastructure/master_cluster"
elif [ -d "/opt/agave" ]; then
    DIR="/opt/agave"
elif [ -f "./Cargo.toml" ]; then
    DIR="$(pwd)"
else
    echo "[!] Error: Project root with Cargo.toml not found." >&2
    exit 1
fi

# Reset Existing Session
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create Session & Capture Immutable Pane IDs
P0=$(tmux new-session -d -s "$SESSION" -n "Proof_Engine" -P -F "#{pane_id}")
P1=$(tmux split-window -h -t "$P0" -P -F "#{pane_id}")
P2=$(tmux split-window -v -t "$P0" -P -F "#{pane_id}")
P3=$(tmux split-window -v -t "$P1" -P -F "#{pane_id}")

# Apply Layout and Visual Themes
tmux select-layout -t "$SESSION" tiled
tmux set -t "$SESSION" pane-border-style fg=brightblack
tmux set -t "$SESSION" pane-active-border-style fg=green
tmux set -t "$SESSION" status-style bg=black,fg=white

# Pane 1: Shred Ingest
tmux send-keys -t "$P0" "cd '$DIR' && clear && echo '=== [PANE 1: RAW UDP SHRED STREAM] ==='" C-m
tmux send-keys -t "$P0" 'RUSTFLAGS="-C target-cpu=native" cargo run --release --bin shred_ingest' C-m

# Pane 2: Sealevel Simulator
tmux send-keys -t "$P1" "cd '$DIR' && clear && echo '=== [PANE 2: HEADLESS SEALEVEL SIMULATOR] ==='" C-m
tmux send-keys -t "$P1" 'RUSTFLAGS="-C target-cpu=native" cargo run --release --bin simulator_shm' C-m

# Pane 3: Bot Depot
tmux send-keys -t "$P2" "cd '$DIR' && clear && echo '=== [PANE 3: BOT DEPOT WORKER EXECUTION] ==='" C-m
if command -v numactl >/dev/null 2>&1; then
    tmux send-keys -t "$P2" 'RUSTFLAGS="-C target-cpu=native" numactl --physcpubind=4-127 cargo run --release --bin bot_depot' C-m
else
    tmux send-keys -t "$P2" 'RUSTFLAGS="-C target-cpu=native" cargo run --release --bin bot_depot' C-m
fi

# Pane 4: System / NUMA Monitor
tmux send-keys -t "$P3" "cd '$DIR' && clear && echo '=== [PANE 4: HARDWARE NUMA & LATENCY PROOF] ==='" C-m
if command -v numastat >/dev/null 2>&1; then
    tmux send-keys -t "$P3" 'watch -n 0.5 numastat -c' C-m
else
    tmux send-keys -t "$P3" 'watch -n 0.5 free -m' C-m
fi

# Attach Session
tmux attach-session -t "$SESSION"
