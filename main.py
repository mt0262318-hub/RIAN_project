cat << 'EOF' > main.py
import os
import sys
import io
import time
import json
import base64
import asyncio
import logging
import re
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from groq import Groq
import edge_tts

load_dotenv()

# ==========================================
# SYSTEM SETTINGS & LOGGING CONFIGURATION
# ==========================================
from config.settings import settings
from config.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger("rian.master_core")

# ==========================================
# R.I.A.N. PHYSICAL PC BRIDGE MANAGER
# ==========================================
class PCBridgeManager:
    def __init__(self):
        self.connected_pc: Optional[WebSocket] = None
        self.main_loop = None
        self._resp_future = None

    async def register(self, websocket: WebSocket):
        self.connected_pc = websocket
        self.main_loop = asyncio.get_running_loop()
        logger.info("⚡ [PC BRIDGE] Windows Laptop Connected successfully!")
        print("⚡ [PC BRIDGE] Windows Laptop Connected successfully!")

    def disconnect(self):
        self.connected_pc = None
        logger.warning("⚠️ [PC BRIDGE] Laptop Disconnected.")
        print("⚠️ [PC BRIDGE] Laptop Disconnected.")

    async def execute_command(self, action: str, target: str = "", params: dict = None) -> dict:
        if not self.connected_pc:
            logger.warning("[PC BRIDGE] Execution failed: Laptop not connected.")
            return {"status": "error", "message": "Laptop Bridge offline."}
        try:
            payload = {"action": action, "target": target}
            if params:
                payload["params"] = params
            await self.connected_pc.send_text(json.dumps(payload))
            return {"status": "success", "message": f"Executed {action} -> {target}"}
        except Exception as e:
            logger.error(f"[PC BRIDGE ERROR] {e}")
            return {"status": "error", "message": str(e)}

    async def handle_response(self, data_str: str):
        try:
            data = json.loads(data_str)
            if self._resp_future and not self._resp_future.done():
                self._resp_future.set_result(data)
        except Exception as e:
            logger.error(f"[BRIDGE PARSE ERROR] {e}")

pc_bridge = PCBridgeManager()

# Link with pc_tools
import tools.pc_tools as pc_tools
pc_tools.set_bridge_instance(pc_bridge)

# ==========================================
# MASTER OS INTENT & CLEANING ENGINE
# ==========================================
def clean_llm_response(text: str) -> str:
    """Removes all thinking tags, thought chains, prompts and reasoning logs"""
    if not isinstance(text, str):
        return str(text)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"Here\'s a thinking process:.*?(?=\n\n|[A-Z][a-z]+:|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"(\*\*Draft.*|\*Draft.*|Output Generation:.*|\[USER\].*|\[RIAN\].*)", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*Final Output:\*\*.*", "", text, flags=re.DOTALL)
    return text.strip()

async def resolve_and_dispatch_action(query: str) -> Optional[str]:
    """Intercepts PC level tasks and directly dispatches them to Windows Bridge"""
    q = (query or "").lower().strip()
    
    if "notepad" in q:
        await pc_bridge.execute_command("open_app", target="notepad")
        return "Notepad open kar diya hai."
    elif "youtube" in q:
        await pc_bridge.execute_command("open_url", target="https://youtube.com")
        return "YouTube open ho gaya."
    elif "edge" in q or "browser" in q or "chrome" in q:
        await pc_bridge.execute_command("open_app", target="msedge")
        return "Browser launch ho raha hai."
    elif "cmd" in q or "terminal" in q:
        await pc_bridge.execute_command("open_app", target="cmd")
        return "Command Prompt start kar diya hai."
    elif "calc" in q or "calculator" in q:
        await pc_bridge.execute_command("open_app", target="calc")
        return "Calculator open ho gaya."
    return None

# ==========================================
# CORE SUBSYSTEMS & ORCHESTRATION ENGINES
# ==========================================
from core.events import event_bus, Event, EventType
from core.session_manager import session_manager
from core.code_sandbox import sandbox
from core.local_llm import local_llm
from core.multi_agent import orchestrator
from core.vector_db import vector_db
from core.vision_engine import vision_engine
from core.persona_manager import persona_engine
from services.ingress_router import ingress_bp
from tools.vault_tool_schema import VAULT_TOOLS, handle_vault_call
from agents.background_monitor import ProactiveMonitor
from agents.graph_builder import build_agent_graph
from services.system_monitor import SystemMonitor
from services.audio_service import AudioService
from tools.base_tools import ALL_TOOLS, load_custom_tools

conversation_history: Dict[str, List[Any]] = {}
processed_requests: Dict[str, float] = {}

RIAN_SYSTEM_PROMPT = """You are R.I.A.N., an elite AI assistant.
Rules:
1. Speak in natural, crisp Hinglish/English.
2. NEVER output your internal thoughts, drafts, or reasoning steps like '<think>' or 'Analyze User Input'.
3. Always give direct, short responses confirming actions taken."""

def get_or_create_history(session_id: str) -> List[Any]:
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    return conversation_history[session_id]

async def generate_rian_response(user_id: str, user_query: str, llm_instance) -> str:
    # 1. Check for Direct PC Action first
    direct_action = await resolve_and_dispatch_action(user_query)
    if direct_action:
        return direct_action

    # 2. Memory & Conversation Execution
    history = get_or_create_history(user_id)
    messages = [SystemMessage(content=RIAN_SYSTEM_PROMPT)]
    messages.extend(history[-6:])
    
    current_user_msg = HumanMessage(content=user_query)
    messages.append(current_user_msg)

    response = await llm_instance.ainvoke(messages)
    clean_reply = clean_llm_response(response.content)

    history.append(current_user_msg)
    history.append(HumanMessage(content=clean_reply))

    if len(history) > 16:
        conversation_history[user_id] = history[-8:]

    return clean_reply

# ==========================================
# MASTER ASSISTANT CLASS
# ==========================================
class RIANAssistant:
    def __init__(self) -> None:
        logger.info("Initializing R.I.A.N. Assistant Master Core...")
        self.llm = ChatGroq(
            model_name="qwen/qwen3.6-27b",
            api_key=settings.groq_api_key or os.environ.get("GROQ_API_KEY", ""),
            temperature=0.4
        )
        self.active_tools = ALL_TOOLS + [
            pc_tools.analyze_laptop_screen,
            pc_tools.play_youtube_video,
            pc_tools.open_system_app_or_file,
            pc_tools.control_pc_hardware,
            pc_tools.type_text_on_laptop,
            pc_tools.write_into_app,
            pc_tools.trigger_hotkey_shortcut,
            pc_tools.control_mouse,
            pc_tools.scroll_screen,
        ] + load_custom_tools()
        self.agent = build_agent_graph(self.llm, self.active_tools)
        self.monitor = SystemMonitor()
        logger.info(f"Loaded {len(self.active_tools)} tools into Agent Execution Graph successfully.")

    async def start(self) -> None:
        await event_bus.start()
        await self.monitor.start()
        logger.info("R.I.A.N. Core & Subsystems are ONLINE.")

    async def stop(self) -> None:
        await self.monitor.stop()
        await event_bus.stop()
        logger.info("R.I.A.N. Systems safely shutdown.")

assistant_instance = RIANAssistant()

# ==========================================
# FASTAPI APPLICATION & UI CONNECTION MANAGER
# ==========================================
app = FastAPI(title="J.I.V.A. / R.I.A.N. Autonomous AI Master")
app.include_router(ingress_bp)

class UIConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        for conn in list(self.active_connections):
            try:
                await conn.send_json(message)
            except Exception:
                pass

ui_manager = UIConnectionManager()

@app.on_event("startup")
async def startup_event():
    await assistant_instance.start()

@app.on_event("shutdown")
async def shutdown_event():
    await assistant_instance.stop()

# ==========================================
# WEBSOCKET CHANNELS (PC BRIDGE + TELEMETRY)
# ==========================================
@app.websocket("/ws/pc-bridge")
async def pc_bridge_route(websocket: WebSocket):
    await websocket.accept()
    await pc_bridge.register(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await pc_bridge.handle_response(data)
    except WebSocketDisconnect:
        pc_bridge.disconnect()
    except Exception:
        pc_bridge.disconnect()

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await ui_manager.connect(websocket)
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                payload = json.loads(data_str)
            except Exception:
                payload = {"query": data_str}

            query = payload.get("query", payload.get("text", payload.get("message", ""))).strip()
            user_id = payload.get("user_id", "web_user_01")

            if not query:
                continue

            # Deduplication Check
            req_id = payload.get("request_id", query)
            now = time.time()
            for r_id, t_stamp in list(processed_requests.items()):
                if now - t_stamp > 6.0:
                    processed_requests.pop(r_id, None)

            if req_id in processed_requests:
                continue
            processed_requests[req_id] = now

            # 1. Update UI Logs
            await websocket.send_json({"type": "log", "log": f"Voice/Text Input: {query}"})
            await websocket.send_json({"type": "state", "agent_status": "PROCESSING", "state_text": "Processing neural command..."})

            # 2. Direct Screen Vision Intercept
            if any(k in query.lower() for k in ["screen", "dekh", "dekho", "kya khula"]):
                vision_out = pc_tools.run_screen_vision(query)
                await websocket.send_json({"type": "response", "reply": vision_out, "text": vision_out})
                continue

            # 3. Resolve Execution & Return Clean Answer
            response_text = await generate_rian_response(
                user_id=user_id,
                user_query=query,
                llm_instance=assistant_instance.llm
            )

            # 4. Broadcast Output
            await websocket.send_json({
                "type": "response",
                "reply": response_text,
                "text": response_text
            })
            await websocket.send_json({
                "type": "state",
                "agent_status": "ACTIVE",
                "state_text": "LISTENING... (Continuous Stream Active)"
            })
    except WebSocketDisconnect:
        ui_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Telemetry WS Error: {e}")
        ui_manager.disconnect(websocket)

# ==========================================
# REST API ENDPOINTS
# ==========================================
@app.post("/api/chat")
async def chat_api(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    query = body.get("query") or body.get("message") or ""
    user_id = body.get("session_id") or body.get("user_id") or "user"
    
    response = await generate_rian_response(user_id, query, assistant_instance.llm)
    return {"status": "success", "user_id": user_id, "response": response}

groq_voice_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

@app.post("/api/voice-query")
async def voice_query_handler(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        transcription = groq_voice_client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes),
            model="whisper-large-v3",
            prompt="Manish, RIAN, Hinglish, Notepad, YouTube, type, open, shortcuts, system commands",
            response_format="json",
        )
        user_text = transcription.text.strip()
        if not user_text:
            return {"user_text": "", "response_text": "I didn't catch that."}

        response_text = await generate_rian_response("voice_user", user_text, assistant_instance.llm)

        communicate = edge_tts.Communicate(response_text, "en-US-ChristopherNeural")
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        audio_stream.seek(0)
        audio_b64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")

        return {
            "user_text": user_text,
            "response_text": response_text,
            "audio_b64": audio_b64,
        }
    except Exception as e:
        logger.error(f"Voice Pipeline Error: {e}")
        return {"user_text": "", "response_text": f"Error: {str(e)}"}

@app.get("/")
def home():
    return {"status": "ONLINE", "system": "R.I.A.N. Autonomous Core"}

# ==========================================
# 3D CYBERPUNK NEURAL INTERFACE (EMBEDDED UI)
# ==========================================
@app.get("/ui", response_class=HTMLResponse)
async def serve_master_ui():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>J.I.V.A. / R.I.A.N. Neural Interface</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Courier New', monospace; user-select: none; }
        body { background: #000308; color: #00e5ff; overflow: hidden; height: 100vh; width: 100vw; position: relative; }
        #canvas3d { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        .hud-glass {
            background: rgba(3, 15, 29, 0.75);
            border: 1px solid rgba(0, 229, 255, 0.45);
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.2), inset 0 0 15px rgba(0, 229, 255, 0.1);
            border-radius: 8px;
            backdrop-filter: blur(14px);
            position: absolute;
            z-index: 10;
        }
        .memory-badge {
            background: rgba(45, 0, 75, 0.65);
            border: 1px solid #bd00ff;
            color: #e29aff;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: bold;
            box-shadow: 0 0 16px rgba(189, 0, 255, 0.5);
            position: absolute;
            z-index: 10;
            letter-spacing: 1px;
        }
        .desktop-status { top: 25px; left: 30px; width: 280px; padding: 18px; }
        .desktop-status h3 { font-size: 16px; letter-spacing: 3px; margin-bottom: 8px; text-shadow: 0 0 10px #00e5ff; }
        .desktop-status p { font-size: 11px; line-height: 1.7; color: #9feeff; }
        .desktop-logs { top: 40px; right: 30px; width: 360px; padding: 18px; }
        .desktop-logs h4 { font-size: 14px; letter-spacing: 2px; margin-bottom: 8px; }
        .log-stream { font-size: 11px; color: #7ce8ff; max-height: 160px; overflow-y: auto; line-height: 1.6; }
        .log-stream::-webkit-scrollbar { width: 4px; }
        .log-stream::-webkit-scrollbar-thumb { background: #00e5ff; border-radius: 2px; }
        .dt-node-1 { top: 40px; right: 410px; }
        .dt-node-2 { top: 120px; right: 400px; }
        .dt-node-3 { bottom: 180px; left: 40px; }
        .dt-node-4 { bottom: 110px; left: 60px; }
        .dt-node-5 { bottom: 130px; right: 90px; }
        .dt-node-6 { bottom: 65px; right: 110px; }
        .desktop-bottom-bar {
            bottom: 25px; left: 50%; transform: translateX(-50%);
            width: 640px; padding: 14px 22px; text-align: center;
            z-index: 20;
        }
        .status-headline { font-size: 12px; font-weight: bold; letter-spacing: 3px; margin-bottom: 10px; text-shadow: 0 0 10px #00e5ff; }
        .input-row { display: flex; gap: 10px; width: 100%; }
        .hud-input {
            flex: 1; background: rgba(0, 18, 32, 0.85); border: 1px solid #00e5ff;
            color: #00e5ff; padding: 10px 14px; border-radius: 6px; outline: none; font-size: 13px;
            box-shadow: inset 0 0 8px rgba(0, 229, 255, 0.2);
        }
        .hud-btn {
            background: rgba(0, 229, 255, 0.25); border: 1px solid #00e5ff; color: #00e5ff;
            padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold;
            transition: 0.2s;
        }
        .hud-btn:hover { background: #00e5ff; color: #000; box-shadow: 0 0 15px #00e5ff; }
    </style>
</head>
<body onclick="engageContinuousVoice()">
    <canvas id="canvas3d"></canvas>
    <div class="desktop-layout">
        <div class="hud-glass desktop-status">
            <h3>SYSTEM R.I.A.N.</h3>
            <p>STATUS: <span style="color:#00ffaa;">ONLINE</span></p>
            <p>NEURAL LINK: ESTABLISHED</p>
            <p>VOICE LOCK: <span style="color:#00ffaa;">ACTIVE (OWNER)</span></p>
        </div>
        <div class="memory-badge dt-node-1">[MEMORY] User_Prefs</div>
        <div class="memory-badge dt-node-2">[CONTEXT] project_Pure_Bal</div>
        <div class="memory-badge dt-node-3">[CONTEXT] Gaura_Purey_Badal</div>
        <div class="memory-badge dt-node-4">[CONTEXT] Active_Session</div>
        <div class="memory-badge dt-node-5">[FILES] project_R.I.A.N_V2.0</div>
        <div class="memory-badge dt-node-6">[MEMORY] Retiles</div>
        <div class="hud-glass desktop-logs">
            <h4>Execution Dashboard</h4>
            <p style="font-size: 10px; color: #9feeff; margin-bottom: 6px;">SYSTEM MONITOR (ACTIVE)</p>
            <div class="log-stream" id="desktopLogStream">
                <div>[SYSTEM] 3D Neural Holo-Core Active.</div>
                <div>[SYSTEM] Telemetry WebSocket Synced.</div>
                <div>[SECURITY] Voice Biometrics Active.</div>
            </div>
        </div>
        <div class="hud-glass desktop-bottom-bar">
            <div class="status-headline" id="desktopStatus">CLICK ANYWHERE TO ENGAGE NEURAL CORE</div>
            <div class="input-row">
                <input type="text" id="desktopInput" class="hud-input" placeholder="Type or speak continuous command..." onkeypress="handleEnter(event, 'desktopInput')" />
                <button class="hud-btn" onclick="sendPrompt(document.getElementById('desktopInput').value, 'desktopInput')">Send</button>
            </div>
        </div>
    </div>
    <script>
        let ws, recognition, voiceStarted = false;
        function connectSocket() {
            const loc = window.location;
            const wsProtocol = loc.protocol === "https:" ? "wss://" : "ws://";
            ws = new WebSocket(wsProtocol + loc.host + "/ws/telemetry");
            ws.onmessage = function(e) {
                const packet = JSON.parse(e.data);
                const logBox = document.getElementById("desktopLogStream");
                if (packet.type === "log" && logBox) {
                    logBox.innerHTML += `<div>[USER] ${packet.log}</div>`;
                    logBox.scrollTop = logBox.scrollHeight;
                }
                if (packet.type === "response") {
                    vocalizeOutput(packet.reply);
                    if (logBox) {
                        logBox.innerHTML += `<div style="color:#00ffaa;">[RIAN] ${packet.reply}</div>`;
                        logBox.scrollTop = logBox.scrollHeight;
                    }
                }
                if (packet.type === "state") {
                    if (document.getElementById("desktopStatus")) document.getElementById("desktopStatus").innerText = packet.state_text;
                }
            };
            ws.onclose = () => setTimeout(connectSocket, 2000);
        }

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas3d'), alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);

        const pCount = 3800;
        const pGeo = new THREE.BufferGeometry();
        const pPos = new Float32Array(pCount * 3);
        for (let i = 0; i < pCount * 3; i += 3) {
            const u = Math.random(), v = Math.random();
            const theta = u * 2.0 * Math.PI, phi = Math.acos(2.0 * v - 1.0);
            const r = 2.2 + (Math.random() * 0.2);
            pPos[i] = r * Math.sin(phi) * Math.cos(theta);
            pPos[i+1] = r * Math.sin(phi) * Math.sin(theta);
            pPos[i+2] = r * Math.cos(phi);
        }
        pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
        const coreMesh = new THREE.Points(pGeo, new THREE.PointsMaterial({ color: 0x00e5ff, size: 0.038, transparent: true, opacity: 0.85 }));
        scene.add(coreMesh);

        const ring1 = new THREE.Mesh(new THREE.RingGeometry(3.0, 3.12, 64), new THREE.MeshBasicMaterial({ color: 0x00e5ff, side: THREE.DoubleSide, transparent: true, opacity: 0.7 }));
        ring1.rotation.x = Math.PI / 2.3;
        scene.add(ring1);

        const ring2 = new THREE.Mesh(new THREE.RingGeometry(3.2, 3.25, 64), new THREE.MeshBasicMaterial({ color: 0x00e5ff, side: THREE.DoubleSide, transparent: true, opacity: 0.4 }));
        ring2.rotation.x = Math.PI / 2.1;
        scene.add(ring2);
        camera.position.z = 6.2;

        function animate() {
            requestAnimationFrame(animate);
            if (coreMesh) { coreMesh.rotation.y += 0.003; coreMesh.rotation.x += 0.001; }
            if (ring1) ring1.rotation.z += 0.0035;
            if (ring2) ring2.rotation.z -= 0.002;
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        function engageContinuousVoice() {
            if (voiceStarted) return;
            voiceStarted = true;
            vocalizeOutput("Systems online Manish. Ready for commands.");
            startVoiceLoop();
        }

        function vocalizeOutput(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                window.speechSynthesis.resume();
                let clean = text.replace(/\[.*?\]/g, '').replace(/[*#_`]/g, '').trim();
                const utt = new SpeechSynthesisUtterance(clean);
                utt.rate = 1.0;
                utt.pitch = 1.0;
                utt.lang = 'hi-IN';
                let voices = window.speechSynthesis.getVoices();
                let v = voices.find(vox => vox.lang.includes('hi') || vox.lang.includes('IN')) || voices[0];
                if (v) utt.voice = v;
                window.speechSynthesis.speak(utt);
            }
        }

        function startVoiceLoop() {
            const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechAPI) return;
            recognition = new SpeechAPI();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.onresult = function(evt) {
                let speechText = '';
                for (let i = evt.resultIndex; i < evt.results.length; ++i) {
                    speechText += evt.results[i][0].transcript;
                }
                const activeInput = document.getElementById('desktopInput');
                if (activeInput) activeInput.value = speechText;
                if (evt.results[evt.results.length - 1].isFinal) {
                    sendPrompt(speechText, 'desktopInput');
                }
            };
            recognition.onerror = () => setTimeout(() => { try { recognition.start(); } catch(e){} }, 800);
            recognition.onend = () => { try { recognition.start(); } catch(e){} };
            try { recognition.start(); } catch(e){}
            if (document.getElementById("desktopStatus")) document.getElementById("desktopStatus").innerText = "LISTENING... (Continuous Stream Active)";
        }

        function handleEnter(e, inputId) {
            if (e.key === 'Enter') {
                sendPrompt(document.getElementById(inputId).value, inputId);
            }
        }

        function sendPrompt(query, inputId) {
            if (!query || !query.trim()) return;
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ query: query, user_id: "web_user_01" }));
            }
            if (inputId && document.getElementById(inputId)) {
                document.getElementById(inputId).value = "";
            }
        }
        window.onload = function() { connectSocket(); };
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

# ==========================================
# MAIN EXECUTION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=True)
EOF
docker restart rian_fastapi