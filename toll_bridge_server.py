#!/usr/bin/env python3
import asyncio
import sqlite3
import time
import os

DB_PATH = "/home/joshua445/sovereign_workspace/toll_bridge.db"
telemetry_queue = asyncio.Queue()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            status TEXT,
            latency_ms REAL,
            timestamp REAL
        );
    """)
    conn.commit()
    conn.close()

async def db_writer_worker():
    """Background task to flush telemetry batch writes from memory to SQLite WAL."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    while True:
        batch = []
        item = await telemetry_queue.get()
        batch.append(item)
        
        # Pull any additional items currently waiting in the queue
        while not telemetry_queue.empty() and len(batch) < 500:
            batch.append(telemetry_queue.get_nowait())
            
        cursor.executemany(
            "INSERT INTO telemetry (client_id, status, latency_ms, timestamp) VALUES (?, ?, ?, ?)",
            batch
        )
        conn.commit()
        for _ in range(len(batch)):
            telemetry_queue.task_done()

async def handle_client(reader, writer):
    t0 = time.perf_counter()
    data = await reader.read(2048)
    if not data:
        writer.close()
        return

    # In-memory validation
    client_id = "unknown"
    for line in data.decode("utf-8", errors="ignore").split("\r\n"):
        if line.lower().startswith("x-client-id:"):
            client_id = line.split(":", 1)[1].strip()
            break

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Non-blocking enqueue to memory queue
    telemetry_queue.put_nowait((client_id, "200_OK", elapsed_ms, time.time()))

    # Instant response return
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 2\r\n"
        "Connection: close\r\n\r\n"
        "OK"
    )
    writer.write(response.encode("utf-8"))
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    init_db()
    asyncio.create_task(db_writer_worker())
    server = await asyncio.start_server(handle_client, "0.0.0.0", 8080)
    print("SIP Toll Bridge Server Active on Port 8080 (Non-Blocking WAL Engine)")
    async in_server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
