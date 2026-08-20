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
                entry = fIPattern: User '{query}' -> Executed via '{action_taken}'"
                if vector_db:
                    await asyncio.to_thread(vector_db.add_texts, [entry], [{"type": "auto_learn", "time": time.time()}])
                self.learned_patterns_count += 1
                self.add_test_log(f"ğŸ§¢´ÄT$äTEÒ–æFW†VC¢w·VW'•³£#×Òâââr"¢W†6WBW†6WF–öã ¢70¢VÆ–b7FGW2ÓÒ'f–ÆVB# ¢6VÆbæFE÷FW7EöÆör†b.(š´UDòÔ„TÅÒæÇ—¦VBf–ÆVC¢w·VW'•³£#×Òâââr" ¢FVbFE÷FW7EöÆör‡6VÆbÂFW‡C¢7G"“ ¢6VÆbæ7F—fU÷FW7G5öÆöræVæB†b%··F–ÖRç7G&gF–ÖR‚rTƒ¢TÓ¦W2r—ÕÒ·FW‡GÒ"¢–bÆVâ‡6VÆbæ7F—fU÷FW7G5öÆör’â#S ¢6VÆbæ7F—fU÷FW7G5öÆörç÷ƒ ¢FVbvWE÷FVÆVÖWG'’‡6VÆb’ÓâF–7E·7G"Âç•Ó ¢&WGW&â°¢&ÆV&æVE÷GFW&ç2#¢6VÆbæÆV&æVE÷GFW&ç5ö6÷VçBÀ¢&F–væ÷7F–75öÆör#¢6VÆbæ7F—fU÷FW7G5öÆöu²Óƒ¥Ğ¢Ğ ¦WFöæöÖ÷W5öÆV&æW"ÒWFöæöÖ÷W4ÆV&æW"‚