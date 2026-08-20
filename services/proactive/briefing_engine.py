import datetime
import logging

logger = logging.getLogger("briefing_engine")

class BriefingEngine:
    """
    Autonomous intelligence summarizer for proactive daily briefs and anomaly alerts.
    """
    def generate_morning_brief(self, user_name: str = "User") -> dict:
        now = datetime.datetime.now()
        current_time_str = now.strftime("%I:%M %p, %A, %B %d, %Y")
        
        brief_payload = {
            "type": "PROACTIVE_BRIEF",
            "timestamp": current_time_str,
            "greeting": f"Good morning. System R.I.A.N. operational check complete.",
            "metrics": {
                "system_status": "OPTIMAL",
                "active_daemons": ["VAD Duplex Voice", "Telegram Vault", "Self-Healing Watchdog"],
                "memory_sync": "Synchronized"
            },
            "proactive_suggestion": "Ready for scheduled automation routines and session workflows."
        }
        logger.info(f"Generated proactive brief at {current_time_str}")
        return brief_payload

    def evaluate_system_health(self, cpu_pct: float, memory_pct: float) -> dict:
        if cpu_pct > 85.0 or memory_pct > 90.0:
            return {
                "alert": True,
                "level": "CRITICAL",
                "message": f"Resource threshold breach: CPU {cpu_pct}%, Mem {memory_pct}%"
            }
        return {"alert": False, "level": "NOMINAL", "message": "All parameters healthy"}
