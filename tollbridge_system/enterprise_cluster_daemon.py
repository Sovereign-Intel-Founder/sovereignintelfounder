import os
import subprocess
import time
import sys
import multiprocessing
import logging

BASE_DIR = "/home/joshua445/tollbridge_system"
LOG_FILE = os.path.join(BASE_DIR, "enterprise_cluster.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ENTERPRISE-SUPERVISOR] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILE)]
)
logger = logging.getLogger("enterprise_supervisor")

os.chdir(BASE_DIR)

def sanitize_infrastructure(ports=[8080, 8888]):
    """Force-release enterprise ports to eliminate address-in-use faults."""
    for port in ports:
        logger.info(f"Enterprise Sanitation: Cleaning port {port}...")
        try:
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, check=False)
            logger.info(f"Port {port} cleared.")
        except Exception as e:
            logger.error(f"Sanitation failed for port {port}: {e}")

def get_enterprise_worker_count():
    cpu_count = multiprocessing.cpu_count()
    enterprise_workers = max(64, int(cpu_count * 0.8))
    logger.info(f"Enterprise Topology: Detected {cpu_count} physical cores. Scaling gateway to {enterprise_workers} worker threads.")
    return enterprise_workers

def launch_enterprise_cluster():
    sanitize_infrastructure([8080, 8888])
    
    worker_count = get_enterprise_worker_count()
    
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
    
    try:
        while True:
            time.sleep(2)
            for name, (cmd, p) in active_processes.items():
                if p.poll() is not None:
                    logger.critical(f"[WATCHDOG] Enterprise service '{name}' failure detected. Emergency restart initiated.")
                    if "simple_forwarder.py" in " ".join(cmd):
                        sanitize_infrastructure([8888])
                    if "gateway_module" in " ".join(cmd):
                        sanitize_infrastructure([8080])
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
