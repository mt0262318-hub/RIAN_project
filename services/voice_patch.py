
import asyncio

async def synthesize_response_audio(text: str):
    # Sends clean text response back to frontend WebSocket for browser-native speech
    return {"type": "voice_reply", "text": text, "status": "ready"}
