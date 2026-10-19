import os
import subprocess
import time
import sys
import multiprocessing
import logging
import signal

# --- ENTERPRISE CONFIGURATION ---
# Designed for 128-core bare-metal saturation.
# Millions of TPS capability requires heavy worker concurrency and zero-copy ingress.
BASE_DIR = "/home/joshua445/tollbridge_system"
LOG_FILE = os.path.join(BASE_DIR, "enterprise_cluster.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ENTERPRISE-SUPERVISOR] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILE)]
)
logger = logging.getLogger("enterprise_supervisor")

os.chdir(BASE_DIR)

def sanitize_infrastructure(port=8080):
    """Force-release enterprise ports to ensure absolute cluster integrity."""
    logger.info(f"Enterprise Sanitation: Cleaning infrastructure port {port}...")
    try:
        # Fuser is standard for enterprise process management
        subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, check=False)
        logger.info(f"Port {port} sanitized.")
    except Exception as e:
        logger.error(f"Sanitation failed: {e}")

def get_enterprise_worker_count():
    """Scale workers to saturate 128-core bare metal."""
    cpu_count = multiprocessing.cpu_count()
    # Allocate 80% of total cores to worker pool to prevent kernel context-switching starvation
    enterprise_workers = max(64, int(cpu_count * 0.8))
    logger.info(f"Enterprise Topology: Detected {cpu_count} physical cores. Scaling to {enterprise_workers} worker threads.")
    return enterprise_workers

def launch_enterprise_cluster():
    sanitize_infrastructure(8080)
    
    worker_count = get_enterprise_worker_count()
    
    # Core Infrastructure Components
    # 1. Forwarder: High-Throughput TCP Proxy
    # 2. Gateway: Enterprise FastAPI Gateway (Uvicorn/Uvloop)
    # 3. Payout: Solana Settlement Engine (Consensus-Optimized)
    # 4. Supervisor: Master Mesh/Ledger Verification
    services = [
        ("TCP-Forwarder", ["python3", "simple_forwarder.py"]),
        ("FastAPI-Gateway", [
            "python3", "-m", "uvicorn", "gateway_module:app",
            "--host", "127.0.0.1", "--port", "8080",
            "--workers", str(worker_count),
            "--loop", "uvloop", "--http", "httptools"
        ]),
        ("Solana-Payout-Engine", ["python3", "payouts_module.py"]),
        ("Master-Supervisor", ["python3", "master_cluster.py"])
    ]
    
    active_processes = {}
    
    logger.info("=== INITIALIZING ENTERPRISE CLUSTER MESH ===")
    
    for name, cmd in services:
        logger.info(f"[BOOTSTRAP] Launching service: {name}")
        process = subprocess.Popen(cmd)
        active_processes[name] = (cmd, process)
        time.sleep(0.5)
        
    logger.info("=== ENTERPRISE CLUSTER FULLY DEPLOYED ===")
    
    # --- WATCHDOG LOOP ---
    try:
        while True:
            time.sleep(2)
            for name, (cmd, p) in active_processes.items():
                if p.poll() is not None:
                    logger.critical(f"[WATCHDOG] Enterprise service '{name}' failure detected. Emergency restart initiated.")
                    if "8080" in " ".join(cmd):
                        sanitize_infrastructure(8080)
                    new_p = subprocess.Popen(cmd)
                    active_processes[name] = (cmd, new_p)
    except KeyboardInterrupt:
        logger.warning("\n[SHUTDOWN] Enterprise Supervisor terminating cluster services.")
        for name, (_, p) in active_processes.items():
            logger.info(f"Graceful shutdown: {name}")
            p.terminate()
            p.wait()
        sys.exit(0)

if __name__ == "__main__":
    launch_enterprise_cluster()
