import asyncio
import time
import uuid
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Callable, Awaitable

class EventType(str, Enum):
    USER_INPUT = "user_input"
    AGENT_RESPONSE = "agent_response"
    TOOL_REQUEST = "tool_request"
    TOOL_RESULT = "tool_result"
    ALERT = "alert"
    REMINDER = "reminder"

@dataclass
class Event:
    type: EventType
    payload: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.subscribers = {}
        self.running = False
        self.logger = logging.getLogger("rian.events")

    def subscribe(self, event_type: EventType, handler: Callable[[Event], Awaitable[None]]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event):
        await self.queue.put(event)

    async def start(self):
        self.running = True
        asyncio.create_task(self._process_events())
        self.logger.info("EventBus started")

    async def stop(self):
        self.running = False
        self.logger.info("EventBus stopped")

    async def _process_events(self):
        while self.running:
            try:
                event = await self.queue.get()
                handlers = self.subscribers.get(event.type, [])
                for handler in handlers:
                    asyncio.create_task(self._safe_handle(handler, event))
                self.queue.task_done()
            except Exception as e:
                self.logger.error(f"Event processing error: {e}")

    async def _safe_handle(self, handler, event):
        try:
            await handler(event)
        except Exception as e:
            self.logger.error(f"Handler error for {event.type}: {e}")

event_bus = EventBus()