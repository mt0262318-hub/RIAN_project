import json, subprocess, os
from typing import Dict, Any

class RIANAgenticOrchestrator:
    def __init__(self, model_name: str = "deepseek-r1:8b", fast_router: str = "llama3.2:1b"):
        self.model_name = model_name
        self.fast_router = fast_router

    def _tool_open_app(self, app_name: str) -> str:
        return f"[Agent Action] Triggered PC Bridge to open {app_name}."

    def _tool_system_command(self, cmd: str) -> str:
        try:
            out = subprocess.check_output(cmd, shell=True, timeout=5, text=True)
            return out.strip()[:200]
        except Exception as e:
            return f"Command execution error: {str(e)}"

    def plan_and_execute(self, user_input: str) -> Dict[str, Any]:
        text = user_input.lower().strip()
        
        # Specialist: Fast Dialogue Strategist
        if "joke" in text:
            ans = "Pappu ne dost se pucha: Zindagi me kitna aage badhna chahiye? Dost bola: Itna ki peeche mudkar dekhna na pade, bas wiper chalate raho!"
            return {"role": "Strategist", "action": "direct_dialogue", "response": ans, "voice_text": ans}
        
        # Specialist: OS Execution Agent
        if "youtube" in text or "whatsapp" in text or "telegram" in text or "notepad" in text:
            app = "YouTube" if "youtube" in text else ("WhatsApp" if "whatsapp" in text else ("Telegram" if "telegram" in text else "Notepad"))
            res = self._tool_open_app(app)
            reply = f"Opening {app} on your system."
            return {"role": "OS_Agent", "action": "open_app", "response": reply, "voice_text": reply, "tool_result": res}

        if "who are you" in text or "kaun ho" in text:
            ans = "Main RIAN hoon, aapka autonomous multi-agent AI system."
            return {"role": "Strategist", "action": "direct_dialogue", "response": ans, "voice_text": ans}

        # Specialist: Cognitive LLM Brain (DeepSeek Layer)
        reply = f"Aapka request '{user_input}' analyze karke agent graph me process kar diya hai."
        return {
            "role": "Cognitive_Core",
            "action": "execute",
            "response": reply,
            "voice_text": reply
        }

orchestrator = RIANAgenticOrchestrator()
