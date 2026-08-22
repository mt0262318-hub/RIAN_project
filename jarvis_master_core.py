import asyncio
import json
import os
import re

# Instant Reflex Actions (<20ms latency bypass)
DIRECT_ACTIONS = {
    "skip": {"action": "skip_song", "params": {}},
    "next": {"action": "skip_song", "params": {}},
    "skip ad": {"action": "skip_ad", "params": {}},
    "ad skip": {"action": "skip_ad", "params": {}},
    "pause": {"action": "media_control", "params": {"command": "play_pause"}},
    "play": {"action": "media_control", "params": {"command": "play_pause"}},
    "volume up": {"action": "media_control", "params": {"command": "volume_up"}},
    "volume down": {"action": "media_control", "params": {"command": "volume_down"}},
    "lock pc": {"action": "lock_pc", "params": {}},
    "minimize": {"action": "window_control", "params": {"command": "minimize"}},
    "maximize": {"action": "window_control", "params": {"command": "maximize"}}
}

class JarvisReflexEngine:
    def __init__(self):
        self.active_context = {}

    def parse_quick_command(self, user_text: str):
        cleaned = user_text.lower().strip()
        
        # 1. Zero-Latency Rule Match
        for trigger, payload in DIRECT_ACTIONS.items():
            if trigger in cleaned:
                return {"type": "reflex", "payload": payload}

        # 2. Dynamic YouTube Handler
        if any(w in cleaned for w in ["play", "gana", "song", "youtube"]):
            query = re.sub(r'(play|chalao|suno|gana|song|youtube|par|lagao|karo)', '', cleaned, flags=re.IGNORECASE).strip()
            return {
                "type": "reflex",
                "payload": {"action": "play_youtube", "params": {"query": query}}
            }

        # 3. Complex Task Routing
        return {
            "type": "complex",
            "prompt": user_text
        }

if __name__ == "__main__":
    engine = JarvisReflexEngine()
    print("[✓] JARVIS High-Speed Reflex Engine Initialized.")
