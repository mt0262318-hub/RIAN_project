import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LocalLLM:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.client:
            return "Groq API key not configured."
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=1024
            )
            raw_res = chat_completion.choices[0].message.content or ""
            # Strip deep thinking tags cleanly
            clean_res = re.sub(r"<think>.*?</think>", "", raw_res, flags=re.DOTALL).strip()
            return clean_res
        except Exception as e:
            return f"Error processing query: {str(e)}"

local_llm = LocalLLM()
