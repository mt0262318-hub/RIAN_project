import asyncio
import logging
from fastapi import APIRouter
from services.proactive.briefing_engine import BriefingEngine

logger = logging.getLogger("heartbeat_daemon")
proactive_router = APIRouter(prefix="/proactive", tags=["Proactive Intelligence"])
brief_engine = BriefingEngine()

@proactive_router.get("/trigger-brief")
async def trigger_proactive_brief():
    brief = brief_engine.generate_morning_brief()
    return {"status": "success", "dispatch": "PROACTIVE_PUSH", "payload": brief}

@proactive_router.get("/heartbeat-health")
async def run_proactive_health_check():
    health = brief_engine.evaluate_system_health(cpu_pct=18.5, memory_pct=42.0)
    return {"status": "success", "evaluation": health}
