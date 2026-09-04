"""
Simple Forwarder: High-throughput asynchronous TCP/UDP proxy and stream forwarder.
"""
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FORWARDER-ENGINE] %(levelname)s: %(message)s"
)
logger = logging.getLogger("forwarder_engine")

class HighThroughputForwarder:
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.host = host
        self.port = port
        self.connections_handled = 0

    async def handle_stream(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info('peername')
        self.connections_handled += 1
        logger.info(f"Established proxy tunnel for peer {peer} (Total: {self.connections_handled})")
        
        try:
            while True:
                chunk = await reader.read(131072) # 128KB buffer chunks
                if not chunk:
                    break
                writer.write(chunk)
                await writer.drain()
        except Exception as e:
            logger.error(f"Stream tunnel error with {peer}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Closed proxy tunnel for peer {peer}")

    async def start(self):
        server = await asyncio.start_server(self.handle_stream, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f"High-Throughput Forwarder listening actively on {addr}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    forwarder = HighThroughputForwarder()
    try:
        asyncio.run(forwarder.start())
    except KeyboardInterrupt:
        logger.info("Forwarder server shut down cleanly.")
