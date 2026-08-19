import logging
import psutil
from langchain_core.tools import tool

logger = logging.getLogger("rian.skills")

@tool
def get_system_stats() -> str:
    """Checks the current CPU usage, RAM usage, and Battery status of the PC."""
    try:
        # 1 second ruk kar accurate CPU percentage nikalna
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # RAM usage nikalna
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        
        # Battery status nikalna (Agar laptop hai toh)
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Charging" if battery.power_plugged else "On Battery"
            battery_status = f"Battery: {battery.percent}% ({plugged})"
        else:
            battery_status = "Battery: No battery detected (Desktop PC)"

        # Final Report
        report = f"Live System Status:\n- CPU Usage: {cpu_usage}%\n- RAM Usage: {ram_usage}%\n- {battery_status}"
        return report
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return f"Error fetching system stats: {e}"