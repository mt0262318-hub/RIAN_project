import subprocess
from datetime import datetime

def run_system_maintenance():
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{log_time}] Starting R.I.A.N. Self-Optimization & Knowledge Check...")
    subprocess.run(["sync"])
    status = subprocess.run(["systemctl", "is-active", "rian-core"], capture_output=True, text=True)
    if "active" not in status.stdout:
        print(f"[{log_time}] rian-core was down. Reviving...")
        subprocess.run(["sudo", "systemctl", "restart", "rian-core"])

if __name__ == "__main__":
    run_system_maintenance()
