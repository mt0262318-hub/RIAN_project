import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from services.vision.vision_engine import VisionContextEngine

logger = logging.getLogger("screen_router")
screen_router = APIRouter(prefix="/vision", tags=["Vision Perception"])
vision_engine = VisionContextEngine()

class FramePayload(BaseModel):
    image_b64: str
    focus_area: str = "full_screen"

@screen_router.post("/ingest-frame")
async def ingest_static_frame(payload: FramePayload):
    result = vision_engine.analyze_screen_frame(payload.image_b64, payload.focus_area)
    return {"status": "success", "result": result}

@screen_router.get("/current-context")
async def get_vision_context():
    return {"status": "success", "context": vision_engine.get_latest_context()}

@screen_router.websocket("/ws/screen-stream")
async def screen_stream_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("🖥️ Screen Vision Stream connected.")
    try:
        while True:
            data = await websocket.receive_json()
            b64_frame = data.get("frame", "")
            focus = data.get("focus", "full_screen")
            
            res = vision_engine.analyze_screen_frame(b64_frame, focus)
            await websocket.send_json({"event": "FRAME_GROUNDED", "analysis": res})
    except WebSocketDisconnect:
        logger.info("🖥️ Screen Vision Stream disconnected.")
    except Exception as e:
        logger.error(f"Screen stream error: {e}")
