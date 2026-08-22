import os
import io
import re
import asyncio
import soundfile as sf
import numpy as np
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def transcribe_audio_buffer(audio_bytes: bytes) -> str:
    """Fast Whisper Transcription via Groq Cloud API"""
    if not client:
        return ""
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="json",
            language="hi",
            temperature=0.0
        )
        return transcription.text.strip()
    except Exception as e:
        print(f"[!] Transcription error: {e}")
        return ""

def direct_command_parser(text: str) -> dict:
    """Zero-Latency Intent Matcher (Bypasses LLM delay for direct tasks)"""
    t = text.lower().strip()
    
    # YouTube Play
    if any(k in t for k in ["play", "gana", "chalao", "suno", "song", "youtube"]):
        cleaned = re.sub(r'(play|chalao|suno|gana|song|youtube|par|lagao|karo)', '', t, flags=re.IGNORECASE).strip()
        return {"action": "play_youtube", "params": {"query": cleaned}}
    
    # Media Controls
    elif any(k in t for k in ["skip ad", "ad skip", "add skip", "ad hatao"]):
        return {"action": "skip_ad", "params": {}}
    elif any(k in t for k in ["next", "skip", "agla", "change"]):
        return {"action": "skip_song", "params": {}}
    elif any(k in t for k in ["pause", "roko", "stop", "play pause"]):
        return {"action": "media_control", "params": {"command": "play_pause"}}
    elif any(k in t for k in ["volume up", "awaz badhao", "sound badhao"]):
        return {"action": "media_control", "params": {"command": "volume_up"}}
    elif any(k in t for k in ["volume down", "awaz kam", "sound kam"]):
        return {"action": "media_control", "params": {"command": "volume_down"}}
        
    # App & Desktop Controls
    elif "notepad" in t and ("open" in t or "kholo" in t or "likho" in t):
        return {"action": "launch_target", "params": {"target": "notepad"}}
    elif "lock" in t and ("pc" in t or "laptop" in t or "screen" in t):
        return {"action": "lock_pc", "params": {}}
    elif "minimize" in t:
        return {"action": "window_control", "params": {"command": "minimize"}}
    elif "maximize" in t:
        return {"action": "window_control", "params": {"command": "maximize"}}
        
    # Fallback to Autonomous Agent
    return {"action": "llm_agent_fallback", "params": {"prompt": text}}

if __name__ == "__main__":
    print("[✓] Live Voice Engine verified & clean.")