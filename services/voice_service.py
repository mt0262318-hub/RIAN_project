import os
import logging
import httpx

logger = logging.getLogger("voice_service")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

async def synthesize_speech(text_content: str, output_path: str = "temp_voice.mp3") -> str:
    """
    Synthesizes speech via ElevenLabs API while maintaining non-blocking async execution.
    """
    if not ELEVENLABS_API_KEY:
        logger.info("ElevenLabs key not configured. Voice dispatch running in text-only mode.")
        return ""

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text_content,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            else:
                logger.error(f"Voice generation failed: HTTP {response.status_code}")
                return ""
    except Exception as e:
        logger.error(f"Voice synthesis error: {e}")
        return ""
