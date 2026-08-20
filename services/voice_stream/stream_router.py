import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.voice_stream.vad_engine import VoiceActivityEngine

logger = logging.getLogger("voice_stream")
stream_router = APIRouter(prefix="/ws/voice", tags=["Duplex Voice"])
vad = VoiceActivityEngine()

@stream_router.websocket("/duplex-stream")
async def websocket_duplex_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🎙️ Duplex Voice Stream connected.")
    
    current_tts_task = None
    
    try:
        while True:
            message = await websocket.receive()
            
            # Handle binary PCM audio frames
            if "bytes" in message and message["bytes"]:
                raw_chunk = message["bytes"]
                speech_detected = vad.is_speech(raw_chunk)
                
                # Barge-in: User speaks while AI is playing audio
                if speech_detected and current_tts_task and not current_tts_task.done():
                    logger.info("⚡ Barge-in: Halting active audio playback.")
                    current_tts_task.cancel()
                    await websocket.send_json({"event": "INTERRUPTED", "msg": "Audio halted"})

                await websocket.send_json({
                    "event": "VAD_STATUS",
                    "speech": speech_detected,
                    "bytes_received": len(raw_chunk)
                })

            # Handle JSON control frames
            elif "text" in message and message["text"]:
                text_payload = message["text"]
                logger.info(f"Voice control event: {text_payload}")
                await websocket.send_json({"event": "ACK", "payload": text_payload})

    except WebSocketDisconnect:
        logger.info("🎙️ Duplex Voice Stream disconnected.")
    except Exception as e:
        logger.error(f"Duplex Stream Exception: {e}")
