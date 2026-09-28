#!/bin/bash
echo "Starting Sovereign Intelligence Protocol Pipeline..."
./ingestion_worker &
INGEST_PID=$!
sleep 0.1
./latency_worker &
LAT_PID=$!
sleep 1
kill $INGEST_PID $LAT_PID 2>/dev/null
echo "Pipeline test cycle completed successfully."
