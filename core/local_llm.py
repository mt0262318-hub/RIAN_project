import requests
import json

class LocalLLMEngine:
    def __init__(self, model_name: str = "llama3:8b-instruct-q4_K_M", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.generate_url = f"{base_url}/api/generate"

    def generate_response(self, prompt: str, system_prompt: str = "You are RIAN, an advanced offline AI assistant.") -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        try:
            response = requests.post(self.generate_url, json=payload, timeout=60)
            if response.status_code == 200:
                import re
        if isinstance(response, str):
            response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        return response.json().get("response", "").strip()
            return f"Error: Local model returned status code {response.status_code}"
        except Exception as e:
            return f"Error communicating with local LLM engine: {str(e)}"

local_llm = LocalLLMEngine()
