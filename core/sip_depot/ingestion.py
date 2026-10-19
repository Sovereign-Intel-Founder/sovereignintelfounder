import time
class DirectFeedIngester:
    def __init__(self):
        # Simulates raw network socket / UDP packet ingestion from venue feeds
        self.packet_sequence = 0

    def poll_raw_feed(self):
        self.packet_sequence += 1
        # Generates a raw market tick frame
        return {
            "seq": self.packet_sequence,
            "recv_timestamp_ns": time.time_ns(),
            "bid": 101.20 if self.packet_sequence % 2 != 0 else 100.10,
            "ask": 100.50 if self.packet_sequence % 2 != 0 else 100.05,
            "depth_a": 18.5,
            "depth_b": 22.1,
            "velocity": 140.0,
            "volatility": 1.2,
            "latency_ms": 3.8,
            "est_slippage": 0.0015,
            "fees": 0.08,
            "node_status": "HEALTHY",
            "entropy": 0.45,
            "route_clear": True,
            "mempool_load": 0.25,
            "finality_delta_ms": 45.0
        }
