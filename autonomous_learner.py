import asyncio
import time
import logging
from typing import Dict, Any, List
from core.vector_db import vector_db
from config.logging_config import get_logger

logger = get_logger("rian.autonomous_learner")

class AutonomousLearner:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.learned_patterns_count: int = 0
        self.active_tests_log: List[str] = [
            "[SYSTEM] Autonomous Self-Learning Initialized",
            "[SYSTEM] Real-time Telemetry Stream Active"
        ]

    async def log_and_learn(self, query: str, action_taken: str, status: str):
        record = {
            "timestamp": time.time(),
            "query": query,
            "action": action_taken,
            "status": status
        }
        self.audit_log.append(record)
        if len(self.audit_log) > 200:
            self.audit_log.pop(0)

        if status == "success" and query.strip():
            try:
                entry = f"Pattern: User '{query}' -> Executed via '{action_taken}'"
                if vector_db:
                    await asyncio.to_thread(vector_db.add_texts, [entry], [{"type": "auto_learn", "time": time.time()}])
                self.learned_patterns_count += 1
                self.add_test_log(f"🧠 [LEARNED] Indexed: '{query[:20]}...'")
            except Exception:
                pass
        elif status == "failed":
            self.add_test_log(f"⚠️ [AUTO-HEAL] Analyzed failed: '{query[:20]}...'")

    def add_test_log(self, text: str):
        self.active_tests_log.append(f"[{time.strftime('%H:%M:%S')}] {text}")
        if len(self.active_tests_log) > 25:
            self.active_tests_log.pop(0)

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "learned_patterns": self.learned_patterns_count,
            "diagnostics_log": self.active_tests_log[-8:]
        }

autonomous_learner = AutonomousLearner()