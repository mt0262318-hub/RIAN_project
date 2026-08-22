import os
import io
import asyncio
import soundfile as sf
import numpy as np
from groq import Groq

# High-Speed Audio-to-Action Parser
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def transcribe_audio_buffer(audio_bytes: bytes) -> str:
    """Sub-300ms Whisper Transcription via Direct Cloud Buffer"""
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
    """Ultra-fast regex & intent rule matching (0ms LLM latency bypass)"""
    t = text.lower().strip()
    
    # YouTube Play
    if any(k in t for k in ["play", "gana", "chalao", "suno", "song", "youtube"]):
        cleaned_query = t
        for stop_word in ["play", "chalao", "suno", "gana", "song", "youtube", "par", "lagao", "karo"]:
            cleaned_query = cleaned_query.replace(stop_word, "")
        return {"action": "play_youtube", "params": {"query": cleaned_query.strip()}}
    
    # Media Controls
    elif any(k in t for k in ["skip ad", "ad skip", "add skip", "ad hatao"]):
        return {"action": "skip_ad", "params": {}}
    elif any(k in t for k in ["next", "skip", "agla gana", "change"]):
        return {"action": "skip_song", "params": {}}
    elif any(k in t for k in ["pause", "roko", "stop", "play pause"]):
        return {"action": "media_control", "params": {"command": "play_pause"}}
    elif any(k in t for k in ["volume up", "awaz badhao", "sound badhao"]):
        return {"action": "media_control", "params": {"command": "volume_up"}}
    elif any(k in t for k in ["volume down", "awaz kam karo", "sound kam karo"]):
        return {"action": "media_control", "params": {"command": "volume_down"}}
        
    # App & Windows Controls
    elif "notepad" in t and ("open" in t or "kholo" in t or "likho" in t):
        return {"action": "launch_target", "params": {"target": "notepad"}}
    elif "lock" in t and ("pc" in t or "laptop" in t or "screen" in t):
        return {"action": "lock_pc", "params": {}}
    elif "minimize" in t:
        return {"action": "window_control", "params": {"command": "minimize"}}
    elif "maximize" in t:
        return {"action": "window_control", "params": {"command": "maximize"}}
        
    # Default fallback to LLM
    return {"action": "llm_agent_fallback", "params": {"prompt": text}}

if __name__ == "__main__":
    print("[✓] Live Voice Engine compiled and ready.")
