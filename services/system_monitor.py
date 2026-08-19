import asyncio
import logging
import psutil
from typing import Optional
from config.settings import settings
from core.events import event_bus, Event, EventType

logger = logging.getLogger("rian.monitor")

class SystemMonitor:
    def __init__(self) -> None:
        self.task: Optional[asyncio.Task] = None
        self.running: bool = False
        logger.info("SystemMonitor initialized")
    
    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info("SystemMonitor started")
    
    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("SystemMonitor stopped")
    
    async def _monitor_loop(self) -> None:
        while self.running:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                ram_percent = psutil.virtual_memory().percent
                
                if cpu_percent > settings.cpu_alert_threshold:
                    await self._send_alert("CPU_HIGH", f"CPU usage at {cpu_percent}%")
                
                if ram_percent > settings.ram_alert_threshold:
                    await self._send_alert("RAM_HIGH", f"RAM usage at {ram_percent}%")
                
                await asyncio.sleep(settings.monitor_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(1)
    
    async def _send_alert(self, alert_type: str, message: str) -> None:
        try:
            alert_event = Event(
                type=EventType.ALERT,
                payload={"alert_type": alert_type, "message": message}
            )
            await event_bus.publish(alert_event)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")