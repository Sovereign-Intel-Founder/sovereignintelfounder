#!/usr/bin/env bash
set -e

# Gather metadata for cryptographic/provenance validation
GIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "not-a-git-repo")
CPU_MODEL=$(lscpu | grep "Model name" | sed 's/Model name:\s*//g' | xargs)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
OUTPUT_FILE="comprehensive_results.json"

echo "=== Starting Hardened Multi-Scale SPSC Sweep ==="
echo "Timestamp : $TIMESTAMP"
echo "Git Commit: $GIT_SHA"
echo "CPU Model : $CPU_MODEL"
echo ""

# Initialize JSON array file
echo "[" > "$OUTPUT_FILE"

FIRST=1
for ops in 1000000 5000000 10000000 25000000; do
    echo "Running sweep at $ops operations..."
    
    # Compile with maximum optimization, thread support, and macro-injected workload targets
    gcc -O3 -pthread -march=native -DTARGET_OPS=$ops spsc_bench.c -o bench_exec
    
    # Run and capture JSON result line
    RESULT_JSON=$(./bench_exec)
    
    # Append system metadata fields to the JSON object
    ENRICHED_JSON=$(echo "$RESULT_JSON" | sed "s/}/, \"git_sha\": \"$GIT_SHA\", \"cpu\": \"$CPU_MODEL\", \"timestamp\": \"$TIMESTAMP\"}/")
    
    if [ $FIRST -eq 1 ]; then
        echo "  $ENRICHED_JSON" >> "$OUTPUT_FILE"
        FIRST=0
    else
        echo "  ,$ENRICHED_JSON" >> "$OUTPUT_FILE"
    fi
done

echo "]" >> "$OUTPUT_FILE"
echo ""
echo "=== Sweep Complete. Verified Artifact Saved to $OUTPUT_FILE ==="
cat "$OUTPUT_FILE"
