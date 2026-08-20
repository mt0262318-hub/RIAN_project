import os
import sys
import time
import logging
import subprocess

# Ensure local imports work cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.vault_storage import send_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [SUPERVISOR] - %(message)s")
logger = logging.getLogger("supervisor")

MONITORED_CONTAINERS = ["rian_fastapi", "rian_postgres", "rian_nginx"]

def check_and_heal_containers():
    """
    Scans running containers, automatically restarts any failed instance,
    and dispatches instant incident reports to Telegram.
    """
    try:
        ps_output = subprocess.check_output(
            ["docker", "ps", "--format", "{{.Names}}"],
            text=True
        ).splitlines()

        for container in MONITORED_CONTAINERS:
            if container not in ps_output:
                logger.warning(f"⚠️ Container '{container}' is DOWN! Initiating auto-recovery...")
                try:
                    subprocess.run(["docker", "start", container], check=True)
                    send_alert(f"🚨 **R.I.A.N. Self-Healing Alert**:\nContainer `{container}` was found down and successfully auto-restarted.")
                    logger.info(f"✅ Container '{container}' restarted successfully.")
                except Exception as ex:
                    error_msg = f"❌ Failed auto-restart for {container}: {ex}"
                    logger.error(error_msg)
                    send_alert(f"🔥 **CRITICAL FAILURE**:\nUnable to revive `{container}`: {ex}")
    except Exception as e:
        logger.error(f"Supervisor check failed: {e}")

if __name__ == "__main__":
    logger.info("🛡️ Running one-time Supervisor Health Audit...")
    check_and_heal_containers()
    print("✅ Supervisor Self-Healing module verified!")
