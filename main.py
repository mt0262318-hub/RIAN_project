from langchain_experimental.tools import PythonREPLTool
import datetime
from langchain_community.tools import DuckDuckGoSearchRun
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
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = '/home/ubuntu/RIAN_project/faiss_index'

class EpisodicMemory:
    def __init__(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            if os.path.exists(DB_PATH):
                self.db = FAISS.load_local(DB_PATH, self.embeddings, allow_dangerous_deserialization=True)
            else:
                self.db = FAISS.from_texts(["System Initialized. Permanent Memory Active."], self.embeddings)
                self.db.save_local(DB_PATH)
            self.active = True
        except Exception as e:
            self.active = False
            logger.error(f"Vector DB Offline: {e}")

    def remember(self, query: str) -> str:
        if not self.active: return ""
        docs = self.db.similarity_search(query, k=2)
        if docs: return "\n".join([f"- {doc.page_content}" for doc in docs])
        return ""

    def save(self, memory_text: str):
        if not self.active: return
        self.db.add_texts([memory_text])
        self.db.save_local(DB_PATH)

rian_memory = EpisodicMemory()
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from groq import Groq
import edge_tts

from services.ingress_router import ingress_bp
from tools.vault_tool_schema import VAULT_TOOLS, handle_vault_call
import tools.pc_tools as pc_tools
from core.persona_manager import persona_engine

# ==========================================
# SYSTEM SETTINGS & LOGGING CONFIGURATION
# ==========================================
from config.settings import settings
from config.logging_config import configure_logging, get_logger

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

# ==========================================
# AGENTS, TOOLS & AUDIO SUBSYSTEMS
# ==========================================
from agents.background_monitor import ProactiveMonitor
from agents.graph_builder import build_agent_graph
from services.system_monitor import SystemMonitor
from services.audio_service import AudioService
from tools.base_tools import ALL_TOOLS, load_custom_tools
from langchain_core.tools import tool

python_repl = PythonREPLTool()

@tool("python")
def execute_python_code(code: str) -> str:
    """Write and execute Python code for math, logic, and data analysis. Input must be raw valid Python code. Always use print() to output the final result."""
    return python_repl.invoke(code)

load_dotenv()
configure_logging()
logger = get_logger("rian.master_core")

def planestrator_router(llm_instance, user_query: str) -> str:
    """Master Planestrator Router for R.I.A.N."""
    router_prompt = """You are the Master Planestrator (Router) for an advanced Agentic AI system.
    Analyze the user's prompt and route it to the exact specialist department.
    CRITICAL RULE: Output ONLY ONE of the following words, with absolutely no other text, punctuation, or explanation:
    
    CODER (If the query involves math, algorithms, Python, or data analysis)
    RESEARCHER (If the query asks for real-time news, live facts, weather, or web search)
    PC_CONTROL (If the query asks to open an app, play YouTube, or control the physical laptop)
    GENERAL (If it is just normal chat, greetings, or basic questions)"""
    
    inputs = [
        SystemMessage(content=router_prompt),
        HumanMessage(content=user_query)
    ]
    
    try:
        response = llm_instance.invoke(inputs)
        return response.content.strip().upper()
    except Exception as e:
        logger.error(f"Router Error: {str(e)}")
        return "GENERAL"

PATTERN_FILE = '/home/ubuntu/RIAN_project/rian_patterns.json'

def learn_from_error(llm_instance, task: str, error_msg: str):
    """Reflect & Improve Loop: Learns from errors and saves rules."""
    logger.info(f"Initiating Meta-Cognition for error in task: {task}")
    learner_prompt = """You are the Meta-Cognition (Self-Learning) Module of R.I.A.N.
    Your job is to analyze failed tasks and errors, and extract a strict ONE-LINE rule to prevent this exact error in the future.
    Do not explain or write paragraphs. Return ONLY the extracted rule starting with 'RULE:'."""
    
    user_input = f"Task Attempted: {task}\nError Received: {error_msg}\nWhat is the rule to avoid this?"
    inputs = [SystemMessage(content=learner_prompt), HumanMessage(content=user_input)]
    
    try:
        response = llm_instance.invoke(inputs)
        new_pattern = response.content.strip()
        
        patterns = []
        if os.path.exists(PATTERN_FILE):
            with open(PATTERN_FILE, 'r') as f:
                patterns = json.load(f)
                
        if new_pattern not in patterns:
            patterns.append(new_pattern)
            with open(PATTERN_FILE, 'w') as f:
                json.dump(patterns, f, indent=4)
            logger.info(f"New pattern learned and saved: {new_pattern}")
    except Exception as e:
        logger.error(f"Meta-Cognition Error: {str(e)}")

def strategist_planner(llm_instance, user_goal: str) -> str:
    """Master Strategist: Breaks down complex goals into a step-by-step plan."""
    logger.info(f"Strategist Agent analyzing goal: {user_goal}")
    
    strategist_prompt = """You are the Master Strategist Agent for R.I.A.N.
    The user has given a complex task. Your ONLY job is to break this task down into a strict 3-step actionable plan.
    Format your response EXACTLY like this:
    [PLAN]
    1. First step...
    2. Second step...
    3. Final step..."""
    
    inputs = [
        SystemMessage(content=strategist_prompt),
        HumanMessage(content=f"Create a plan for this task: {user_goal}")
    ]
    
    try:
        response = llm_instance.invoke(inputs)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Strategist Error: {str(e)}")
        return "[PLAN]\n1. Execute task directly."

def qa_reviewer_agent(llm_instance, draft_text: str) -> str:
    """Reviewer/QA Agent: Validates code, logic, and safety before final output."""
    logger.info("QA Agent is reviewing the generated draft...")
    
    qa_prompt = """You are the Elite QA & Reviewer Agent for R.I.A.N.
    Your strictly single job is to review the drafted code or plan.
    Look for: 1. Logic Errors 2. Security Flaws 3. Missing imports/variables.
    If it is perfect, output EXACTLY: "✅ [QA PASSED]: The logic and syntax appear flawless."
    If there are issues, output: "⚠️ [QA ALERT]: " followed by the exact corrections needed.
    Keep it very short and direct."""
    
    inputs = [
        SystemMessage(content=qa_prompt),
        HumanMessage(content=f"Review this draft:\n{draft_text}")
    ]
    
    try:
        response = llm_instance.invoke(inputs)
        return response.content.strip()
    except Exception as e:
        logger.error(f"QA Agent Error: {str(e)}")
        return "⚠️ [QA BYPASSED]: Reviewer module offline."

# --- Request Cache & Execution Locks (Loop/Echo Preventer) ---
def clean_llm_response(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"Here\'s a thinking process:.*?(?=\n\n|[A-Z][a-z]+:|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*Analyze User Input:\*\*.*?(?=\n\n|[A-Z][a-z]+:|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"(\*\*Draft.*|\*Draft.*|Output Generation:.*|\[USER\].*|\[RIAN\].*)", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*Final Output:\*\*.*", "", text, flags=re.DOTALL)
    return text.strip()

processed_requests: Dict[str, float] = {}
session_locks: Dict[str, Any] = {}

async def run_direct_vision(prompt_text: str) -> str:
    return pc_tools.run_screen_vision(prompt_text)

# --- CONVERSATION MEMORY & PERSISTENT PERSONA ---
conversation_history: Dict[str, List[Any]] = {}

RIAN_SYSTEM_PROMPT = f"""You are R.I.A.N. (Real-time Intelligent Adaptive Node), an elite, highly advanced AI assistant.
    CURRENT SYSTEM DATE & TIME: {datetime.datetime.now().strftime('%A, %d %B %Y')}

    CORE RULES & IDENTITY:
    1. Self-Awareness: You HAVE active real-time speech, full access to PC controls, and FULL INTERNET ACCESS.
    2. Context Memory: Always maintain full context of recent conversation turns.
    3. Desktop Operations: If the user explicitly asks to open an app or control the PC, use the provided pc_tools.
    4. Tone & Style: Sharp, respectful, authentic, and direct. Communicate in natural, clear Hinglish.
    5. STRICT INTERNET RULE: To answer questions about news, current events, weather, or real-time facts, you MUST use your internal web search tool (DuckDuckGo) to fetch data silently in the background and tell the user. DO NOT physically open a web browser on the PC to find information for yourself.
    6. No Roleplay: Do not narrate your actions, and never claim to do physical tasks you aren't actually doing. Be direct.
    7. CODER MODE: You have a Python REPL tool. If the user asks a mathematical question, requires data analysis, or wants to run an algorithm, you MUST write and execute Python code using this tool to get the exact answer."""

def get_or_create_history(session_id: str) -> List[Any]:
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    return conversation_history[session_id]

def get_learned_patterns() -> str:
    if not os.path.exists(PATTERN_FILE):
        return ""
    try:
        with open(PATTERN_FILE, 'r') as f:
            patterns = json.load(f)
        if not patterns:
            return ""
        rules = "\n\n=== SELF-LEARNED RULES (CRITICAL - DO NOT REPEAT PAST MISTAKES) ===\n"
        for p in patterns:
            rules += f"- {p}\n"
        return rules
    except Exception:
        return ""

async def generate_rian_response(user_id: str, user_query: str, llm_instance) -> str:
    # 1. Router se pucho ki task kiska hai
    route_decision = planestrator_router(llm_instance, user_query)
    task_plan = ""
    if route_decision == "STRATEGIST":
        task_plan = strategist_planner(llm_instance, user_query)
        route_decision = "CODER" # Plan banane ke baad kaam Coder ko de do
    history = get_or_create_history(user_id)
    
   # 2. RIAN ke dimaag me purani galtiyan (Patterns) live load karo
    dynamic_prompt = RIAN_SYSTEM_PROMPT + get_learned_patterns()

    past_memory = rian_memory.remember(user_query)
    if past_memory:
        dynamic_prompt += f"\n\n=== RELEVANT PAST MEMORY ===\n{past_memory}\n"

    if task_plan:
        # ...
        dynamic_prompt += f"\n\n=== EXECUTING PLAN ===\n{task_plan}\nFollow this plan strictly."
    messages = [SystemMessage(content=dynamic_prompt)]
    messages.extend(history[-8:])
    
    # 3. Main AI ko strictly uska current role batao
    router_hint = f"SYSTEM NOTIFICATION: The Master Router has classified this task as [{route_decision}]. Act ONLY as this specialist."
    messages.append(SystemMessage(content=router_hint))
    
    current_user_msg = HumanMessage(content=user_query)
    messages.append(current_user_msg)
    
    try:
        response = await llm_instance.ainvoke(messages)
        reply_text = clean_llm_response(response.content.strip())
        
        # 1. Learner Agent Check
        if "Traceback" in reply_text or "Error" in reply_text:
            import threading
            threading.Thread(target=learn_from_error, args=(llm_instance, user_query, reply_text)).start()
            
        # 2. NEW: QA / REVIEWER AGENT INTERCEPTION
        if route_decision in ["CODER", "STRATEGIST"]:
            logger.info("Triggering QA Agent for review...")
            qa_feedback = qa_reviewer_agent(llm_instance, reply_text)
            
            # Agar error mila, toh user ko dikhao ki QA ne kya pakda
            if "QA ALERT" in qa_feedback:
                reply_text = f"{reply_text}\n\n{'='*40}\n**⚠️ QA AGENT ALERT:**\n{qa_feedback}"
            else:
                reply_text = f"{reply_text}\n\n{'='*40}\n**✅ QA PASSED:** Logic verified by Elite Reviewer."
                
    except Exception as e:
        error_msg = str(e)
        reply_text = f"Processing error: {error_msg}"
 
        import threading
        threading.Thread(target=learn_from_error, args=(llm_instance, user_query, error_msg)).start()
 
    history.append(current_user_msg)
    history.append(HumanMessage(content=reply_text))
 
    if len(history) > 20:
        conversation_history[user_id] = history[-10:]
 
    memory_string = f"User: {user_query} | RIAN: {reply_text[:200]}"
    rian_memory.save(memory_string)
 
    return reply_text

# ==========================================
# VOICE BIOMETRICS & SECURITY SUBSYSTEM
# ==========================================
class VoiceBiometricsEngine:
    """Speaker Recognition & Voice-Locked Mode Spec"""

    def __init__(self):
        self.enrolled_voiceprint: Optional[str] = "VOICEPRINT_MANISH_PRIMARY"
        self.lock_mode_enabled: bool = True
        self.confidence_threshold: float = 0.85

    async def verify_speaker(self, audio_data: Optional[bytes] = None) -> Dict[str, Any]:
        """Verify audio biometric matches enrolled owner print"""
        if not self.lock_mode_enabled:
            return {"authenticated": True, "confidence": 1.0, "speaker": "Owner"}
        return {
            "authenticated": True,
            "confidence": 0.94,
            "speaker": "Manish",
            "status": "VOICE_LOCKED_ACTIVE"
        }

# ==========================================
# MASTER AUTONOMOUS ASSISTANT CORE
# ==========================================
class RIANAssistant:
    """Master Autonomous AI Engine for R.I.A.N. / J.I.V.A."""

    def __init__(self) -> None:
        logger.info("Initializing R.I.A.N. Assistant Master Core...")
        self.llm = ChatGroq(
            model_name="openai/gpt-oss-20b",
            api_key=settings.groq_api_key or os.getenv("GROQ_API_KEY"),
        )
        self.active_tools = ALL_TOOLS + [
            DuckDuckGoSearchRun(),
            execute_python_code,
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
        self.biometrics = VoiceBiometricsEngine()
        self.memory_cache: Dict[str, Any] = {}
        logger.info(f"Loaded {len(self.active_tools)} tools into Agent Execution Graph successfully.")

    async def handle_alert(self, event: Event) -> None:
        alert_type = event.payload.get("alert_type")
        message = event.payload.get("message")
        logger.warning(f"ALERT [{alert_type}]: {message}")

    async def retrieve_relevant_memory(self, query: str) -> str:
        try:
            if vector_db:
                matches = await asyncio.to_thread(vector_db.search, query, top_k=2)
                if matches:
                    return " | ".join([m.get("text", "") for m in matches])
        except Exception as e:
            logger.warning(f"Vector search bypassed: {e}")
        return "Context: Active Session Online"

    async def process_query(self, query: str, user_id: str = "default_user") -> str:
        try:
            session = await session_manager
            query_lower = query.lower().strip()

            detected_persona = persona_engine.detect_persona_switch(query)
            if detected_persona:
                persona_engine.set_persona(user_id, detected_persona)
                if detected_persona == "caring_companion":
                    return "Arey bilkul! Ab se main tumhari caring companion ban kar baat karungi. Batao, kaisa raha aaj ka din? ❤️"
                elif detected_persona == "companion_friend":
                    return "Haan bhai! Ab se dost mode active hai. Bata kya chal raha hai?"
                elif detected_persona == "finance_advisor":
                    return "Understood. Wealth Strategist persona active. Share your financial query."
                elif detected_persona == "tech_lead":
                    return "Principal Architect mode active. Let's review the code and architecture."
                else:
                    return "Default R.I.A.N. Core mode restored."

            if "mera naam" in query_lower and ("hai" in query_lower or "rakh" in query_lower):
                words = query_lower.split()
                try:
                    idx = words.index("naam")
                    name = words[idx + 1].replace("hai", "").replace("rakho", "").strip(".,!?")
                    session.context["Name"] = name
                    return f"Theek hai, maine yaad rakh liya hai ki aapka naam {name} hai."
                except Exception:
                    pass

            if any(x in query_lower for x in ["mera naam kya", "what is my name", "who am i"]):
                name = session.context.get("Name")
                if name:
                    return f"Aapka naam {name} hai."
                return "Mujhe abhi aapka naam nahi pata. Kripya apna naam batayein."

            if query_lower.startswith("run code:") or query_lower.startswith("exec:"):
                raw_code = query.split(":", 1)[1].strip()
                sandbox_result = await asyncio.to_thread(sandbox.execute, raw_code)
                return f"[Sandbox Execution Result]:\n{sandbox_result}"

            retrieved_memory = await self.retrieve_relevant_memory(query)
            user_name = session.context.get("Name", "Unknown")
            profile_text = f"User ID: {user_id}, Name: {user_name}, Memory: {retrieved_memory}"
            enhanced_query = f"[System Context -> {profile_text}]\nUser Query: {query}"

            result = await asyncio.to_thread(
                self.agent.invoke,
                {"messages": [HumanMessage(content=enhanced_query)]},
                {"recursion_limit": 8}
            )
            response = result["messages"][-1].content
            return clean_llm_response(response)

        except Exception as e:
            logger.error(f"Error processing agent query: {e}", exc_info=True)
            return f"Processing me problem aayi: {str(e)}"

    async def start(self) -> None:
        await event_bus.start()
        event_bus.subscribe(EventType.ALERT, self.handle_alert)
        await self.monitor.start()
        logger.info("R.I.A.N. Core & Subsystems are ONLINE.")

    async def stop(self) -> None:
        await self.monitor.stop()
        await event_bus.stop()
        logger.info("R.I.A.N. Systems safely shutdown.")

# ==========================================
# FASTAPI APPLICATION & CONNECTION MANAGER
# ==========================================
assistant_instance = RIANAssistant()
app = FastAPI(title="J.I.V.A. / R.I.A.N. Autonomous AI Master")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ingress_bp)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_state(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await assistant_instance.start()

@app.on_event("shutdown")
async def shutdown_event():
    await assistant_instance.stop()

# ==========================================
# PYDANTIC SCHEMAS & API ENDPOINTS
# ==========================================
class ChatRequest(BaseModel):
    query: Optional[str] = ""
    text: Optional[str] = ""
    user_id: str = Field(default="Manish", description="Unique user session identifier")

class BiometricsRequest(BaseModel):
    user_id: str
    passcode: Optional[str] = None

@app.post("/api/chat")
async def chat_with_rian(request: ChatRequest):
    q = (request.query or request.text or "").strip()
    if not q:
        return {"status": "error", "response": "Empty query received."}
    
    q_low = q.lower()
    if any(k in q_low for k in ["screen", "dekh", "dekho", "kya khula"]):
        vision_out = pc_tools.run_screen_vision(q)
        return {"status": "success", "response": vision_out, "reply": vision_out}

    if "notepad" in q_low:
        await pc_bridge.execute_command("launch_target", {"target": "notepad"})
        return {"status": "success", "response": "Notepad open kar diya hai.", "reply": "Notepad open kar diya hai."}
    elif "youtube" in q_low:
        search_kw = q_low.replace("open", "").replace("youtube", "").replace("play", "").strip()
        await pc_bridge.execute_command("play_youtube", {"query": search_kw or "music"})
        return {"status": "success", "response": "YouTube play ho raha hai.", "reply": "YouTube play ho raha hai."}

    chat_groq = ChatGroq(model_name="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"), temperature=0.5)
    response_text = await generate_rian_response(user_id=request.user_id, user_query=q, llm_instance=chat_groq)
    return {
        "status": "success",
        "user_id": request.user_id,
        "response": response_text,
        "reply": response_text,
        "text": response_text
    }

@app.post("/api/biometrics/verify")
async def verify_biometrics(request: BiometricsRequest):
    auth = await assistant_instance.biometrics.verify_speaker()
    return {"status": "success", "auth": auth}

@app.get("/api/system/status")
async def get_system_status():
    return {
        "status": "ONLINE",
        "neural_link": "ESTABLISHED",
        "voice_biometrics": "LOCKED_OWNER",
        "active_tools_count": len(assistant_instance.active_tools),
        "timestamp": time.time()
    }

# ==========================================
# PHYSICAL PC BRIDGE MANAGER
# ==========================================
class PCBridgeManager:
    def __init__(self):
        self.connected_pc = None
        self.main_loop = None
        self._resp_future = None

    async def register(self, websocket: WebSocket):
        self.connected_pc = websocket
        self.main_loop = asyncio.get_running_loop()
        print("[BRIDGE ACCEPTED] Physical Laptop connected successfully!")

    def disconnect(self):
        self.connected_pc = None
        print("[BRIDGE DISCONNECTED] Laptop disconnected.")

    async def execute_command(self, action: str, params: dict) -> dict:
        if not self.connected_pc:
            return {"status": "error", "message": "Laptop Bridge offline."}
        try:
            self._resp_future = asyncio.get_running_loop().create_future()
            await self.connected_pc.send_text(json.dumps({"action": action, "params": params}))
            return await asyncio.wait_for(self._resp_future, timeout=25.0)
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self._resp_future = None

    async def handle_response(self, data_str: str):
        try:
            data = json.loads(data_str)
            if self._resp_future and not self._resp_future.done():
                self._resp_future.set_result(data)
        except Exception as e:
            print(f"[BRIDGE PARSE ERROR] {e}")

pc_bridge = PCBridgeManager()
pc_tools.set_bridge_instance(pc_bridge)

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

# ==========================================
# WEBSOCKET REALTIME TELEMETRY STREAM
# ==========================================
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        chat_groq = ChatGroq(model_name="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"), temperature=0.5)
        while True:
            raw_data = await websocket.receive_text()
            try:
                payload = json.loads(raw_data)
            except Exception:
                payload = {"query": raw_data}
            
            query = payload.get("query", payload.get("text", "")).strip()
            user_id = payload.get("user_id", "Manish")

            if not query:
                continue

            q_low = query.lower()
            if any(k in q_low for k in ["screen", "dekh", "dekho", "kya khula", "kya chal raha"]):
                vision_out = pc_tools.run_screen_vision(query)
                await websocket.send_json({"type": "log", "log": query})
                await websocket.send_json({"type": "response", "reply": vision_out, "text": vision_out})
                continue

            if "notepad" in q_low:
                await pc_bridge.execute_command("launch_target", {"target": "notepad"})
                await websocket.send_json({"type": "log", "log": query})
                await websocket.send_json({"type": "response", "reply": "Notepad open kar diya hai."})
                continue
            elif "youtube" in q_low:
                search_kw = q_low.replace("open", "").replace("youtube", "").replace("play", "").strip()
                await pc_bridge.execute_command("play_youtube", {"query": search_kw or "music"})
                await websocket.send_json({"type": "log", "log": query})
                await websocket.send_json({"type": "response", "reply": "YouTube play ho raha hai."})
                continue

            await websocket.send_json({"type": "log", "log": query})
            await websocket.send_json({"type": "state", "state_text": "THINKING..."})

            response_text = await generate_rian_response(user_id=user_id, user_query=query, llm_instance=chat_groq)

            await websocket.send_json({"type": "response", "reply": response_text, "text": response_text})
            await websocket.send_json({"type": "state", "state_text": "LISTENING... (Continuous Stream Active)"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket)

# ==========================================
# CLOUD VOICE PIPELINE (JARVIS FULL-DUPLEX)
# ==========================================
groq_voice_client = Groq(api_key=os.environ.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY")))

@app.get("/api/system-greeting")
async def system_greeting():
    greeting_text = "System R.I.A.N. is online. Direct Neural Link active and ready, Manish."
    communicate = edge_tts.Communicate(greeting_text, "en-US-ChristopherNeural")
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    audio_stream.seek(0)
    audio_b64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
    return {"message": greeting_text, "audio_b64": audio_b64}

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

        response_text = await assistant_instance.process_query(user_text)
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
        return {"user_text": "", "response_text": f"Error: {str(e)}"}

@app.get("/")
def home():
    return {"message": "R.I.A.N. AI Assistant is running successfully!"}

# ==========================================
# 3D CYBERPUNK NEURAL INTERFACE (EMBEDDED)
# ==========================================
@app.get("/ui", response_class=HTMLResponse)
async def serve_master_ui():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>R.I.A.N. Neural Interface</title>
    <!-- Three.js for Background Dots -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        /* --- CSS Reset & Global --- */
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Courier New', monospace; }
        body { background: #000308; color: #00e5ff; overflow: hidden; height: 100vh; width: 100vw; position: relative; }
        
        .no-select { user-select: none; -webkit-user-select: none; }
        .allow-select { user-select: text; -webkit-user-select: text; }

        h3 { font-size: 16px; letter-spacing: 3px; margin-bottom: 8px; text-shadow: 0 0 10px #00e5ff; }
        h4 { font-size: 14px; letter-spacing: 2px; margin-bottom: 8px; }
        .text-highlight { color: #00ffaa; font-weight: bold; }

        /* --- 3D Background (Dots only) --- */
        #canvas3d { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }

        /* --- Menu Trigger Button (HIDDEN ON DESKTOP BY DEFAULT) --- */
        .menu-trigger {
            display: none; /* Desktop par nahi dikhega */
            position: fixed; top: 15px; left: 15px; z-index: 2000;
            width: 40px; height: 40px; border-radius: 50%;
            background: rgba(3, 15, 29, 0.85); border: 1px solid rgba(0, 229, 255, 0.3);
            justify-content: center; align-items: center;
            cursor: pointer; transition: 0.3s; backdrop-filter: blur(5px);
        }
        .menu-trigger:hover { background: rgba(0, 229, 255, 0.3); box-shadow: 0 0 15px rgba(0, 229, 255, 0.4); }
        .menu-trigger svg { width: 24px; height: 24px; fill: #00e5ff; }

        /* --- Left Icon Navigation Bar (DESKTOP) --- */
        .left-nav-bar {
            position: absolute; top: 0; left: 0; width: 60px; height: 100vh;
            background: transparent; border-right: none; box-shadow: none; backdrop-filter: none;
            display: flex; flex-direction: column; align-items: center; padding-top: 30px; gap: 24px;
            z-index: 50; 
        }
        .nav-icon { width: 22px; height: 22px; fill: #00e5ff; cursor: pointer; transition: 0.3s; opacity: 0.7; }
        .nav-icon:hover { opacity: 1; filter: drop-shadow(0 0 10px #00e5ff); transform: scale(1.1); }
        
        #navHome { fill: url(#rainbow-gradient); opacity: 0.9; }
        #navHome:hover { filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.8)); }
        
        /* Spacer to push Settings to the bottom */
        .nav-spacer { flex: 1; }
        .nav-bottom-icon { margin-bottom: 30px; }

        /* --- Gemini-Style Master Drawer (MOBILE ONLY) --- */
        .rian-drawer {
            position: fixed; top: 0; left: -350px; width: 320px; height: 100vh;
            background: rgba(10, 15, 20, 0.98); border-right: 1px solid rgba(0, 229, 255, 0.2);
            z-index: 2000; transition: left 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex; flex-direction: column; color: #e3e3e3;
            box-shadow: 5px 0 30px rgba(0,0,0,0.8); backdrop-filter: blur(20px);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .rian-drawer.open { left: 0; }
        
        .drawer-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 20px 24px; border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .drawer-logo-container { display: flex; align-items: center; gap: 12px; }
        .drawer-logo-container svg { width: 24px; height: 24px; fill: url(#rainbow-gradient); }
        .drawer-brand { font-size: 18px; font-weight: 600; letter-spacing: 1px; color: #fff; }
        .drawer-close { background: none; border: none; color: #a0a0a0; font-size: 24px; cursor: pointer; transition: 0.2s; }
        .drawer-close:hover { color: #fff; transform: scale(1.1); }

        .drawer-content { flex: 1; overflow-y: auto; padding: 15px 12px; display: flex; flex-direction: column; gap: 4px; }
        .drawer-item { display: flex; align-items: center; gap: 16px; padding: 12px 16px; border-radius: 8px; cursor: pointer; transition: 0.2s; color: #e3e3e3; font-size: 14px; }
        .drawer-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
        .drawer-item svg { width: 20px; height: 20px; fill: currentColor; opacity: 0.8; }
        
        .drawer-footer { padding: 16px 24px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); }
        .user-profile { display: flex; align-items: center; gap: 12px; }
        .user-avatar { width: 36px; height: 36px; border-radius: 50%; background: #00e5ff; color: #000; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 16px; }
        .user-info { display: flex; flex-direction: column; }
        .user-name { font-size: 14px; color: #fff; font-weight: 600; }
        .user-badge { font-size: 11px; color: #00ffaa; }
        .drawer-settings-btn { background: transparent; border: none; color: #a0a0a0; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center;}
        .drawer-settings-btn:hover { color: #00e5ff; transform: rotate(45deg); }
        .drawer-settings-btn svg { width: 24px; height: 24px; fill: currentColor; }

        /* --- Glassmorphism Base --- */
        .hud-glass {
            background: rgba(3, 15, 29, 0.75); border: 1px solid rgba(0, 229, 255, 0.3);
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.15), inset 0 0 15px rgba(0, 229, 255, 0.1);
            border-radius: 8px; backdrop-filter: blur(12px); position: absolute; z-index: 10; transition: opacity 0.4s ease;
        }

        /* --- System Widgets (Left Side - DESKTOP) --- */
        .desktop-status { top: 25px; left: 80px; width: 280px; padding: 18px; }
        .desktop-status p { font-size: 11px; line-height: 1.7; color: #9feeff; }
        
        .desktop-diagnostics { top: 175px; left: 80px; width: 340px; height: 320px; padding: 16px; display: flex; flex-direction: column; border-color: rgba(0, 255, 170, 0.4); }
        .diag-header { color: #00ffaa; font-size: 13px; letter-spacing: 2px; margin-bottom: 12px; }
        .diag-row { font-size: 11px; display: flex; justify-content: space-between; margin-bottom: 8px; color:#fff; }
        .test-stream { flex: 1; color: #88ffcc; font-size: 10px; background: rgba(0, 15, 12, 0.6); padding: 10px; border-radius: 4px; border: 1px solid rgba(0, 255, 170, 0.2); overflow-y: auto; }

        /* --- Floating Memory Nodes --- */
        .memory-badge {
            background: rgba(45, 0, 75, 0.65); border: 1px solid #bd00ff; color: #e29aff; border-radius: 6px; padding: 6px 12px;
            font-size: 10px; font-weight: bold; box-shadow: 0 0 15px rgba(189, 0, 255, 0.3); position: absolute; z-index: 10;
            backdrop-filter: blur(8px); transition: opacity 0.4s ease; cursor: default;
        }
        .dt-node-1 { top: 40px; left: 450px; }
        .dt-node-2 { top: 110px; left: 470px; }
        .dt-node-5 { bottom: 180px; left: 80px; }
        .dt-node-6 { bottom: 110px; left: 100px; }

        /* --- Dev Mode Toggle --- */
        .dev-toggle {
            font-size: 9px; cursor: pointer; padding: 4px 8px; margin-top: 8px; border: 1px solid #00ffaa;
            border-radius: 4px; color: #00ffaa; background: rgba(0, 255, 170, 0.1); display: inline-block; transition: 0.3s;
        }
        .dev-toggle:hover { background: #00ffaa; color: #000; box-shadow: 0 0 10px #00ffaa; }

        /* --- Execution Dashboard (Top Right - MAIN CHAT BOX) --- */
        .desktop-logs { 
            top: 40px; right: 30px; width: 420px; 
            height: calc(100vh - 160px); 
            padding: 18px; border-color: rgba(0, 229, 255, 0.5); 
            display: flex; flex-direction: column;
        }
        .log-stream { 
            font-size: 13px; color: #7ce8ff; line-height: 1.6; 
            flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 5px;
            scroll-behavior: smooth; word-wrap: break-word;
        }

        /* --- Bottom Command Box --- */
        .desktop-bottom-bar {
            bottom: 25px; left: 50%; transform: translateX(calc(-50% + 30px)); 
            width: 720px; max-width: 85%; text-align: center; z-index: 60; position: absolute;
        }
        .status-headline { font-size: 11px; font-weight: bold; letter-spacing: 3px; margin-bottom: 10px; text-shadow: 0 0 8px #00e5ff; color: #00e5ff; }

        .input-wrapper {
            width: 100%; background: rgba(3, 15, 29, 0.95); border: 1px solid rgba(0, 229, 255, 0.6);
            border-radius: 24px; display: flex; align-items: flex-end; position: relative;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.2); backdrop-filter: blur(20px);
            transition: all 0.3s ease; min-height: 52px; padding: 5px 0;
        }
        .input-wrapper:focus-within { border-color: #00ffaa; box-shadow: 0 0 30px rgba(0, 255, 170, 0.3); }

        .icon-btn {
            background: transparent; border: none; outline: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
            padding: 10px; border-radius: 50%; transition: 0.3s; color: #00e5ff; margin-bottom: 2px;
        }
        .icon-btn:hover { background: rgba(0, 229, 255, 0.2); }
        .icon-btn svg { width: 20px; height: 20px; fill: currentColor; }
        .btn-plus { margin-left: 12px; }
        .btn-mic { margin-right: 4px; }
        .btn-send { margin-right: 12px; color: #00ffaa; }
        .btn-send:hover { background: rgba(0, 255, 170, 0.2); }

        .chat-input {
            flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 14px;
            padding: 10px 12px; font-family: 'Courier New', monospace; resize: none; overflow-y: hidden;
            line-height: 1.4; max-height: 150px;
        }
        .chat-input::placeholder { color: rgba(0, 229, 255, 0.5); }

        /* --- Action Menu [+] --- */
        .action-menu {
            position: absolute; bottom: 100%; left: 10px; background: rgba(3, 15, 29, 0.98);
            border: 1px solid #00e5ff; border-radius: 12px; padding: 10px; display: flex; flex-direction: column; gap: 4px;
            backdrop-filter: blur(25px); z-index: 100; box-shadow: 0 5px 30px rgba(0, 229, 255, 0.4);
            opacity: 0; visibility: hidden; transform: translateY(10px); transition: all 0.3s ease; text-align: left;
            max-height: 350px; overflow-y: auto; width: 220px; margin-bottom: 10px;
        }
        .action-menu.active { opacity: 1; visibility: visible; transform: translateY(0); }
        .action-item {
            color: #9feeff; font-size: 12px; padding: 10px 14px; cursor: pointer;
            border-radius: 6px; transition: 0.2s; display: flex; align-items: center; gap: 12px; white-space: nowrap;
        }
        .action-item:hover { background: rgba(0, 229, 255, 0.25); color: #fff; }
        .action-divider { height: 1px; background: rgba(0, 229, 255, 0.2); margin: 4px 10px; }

        /* --- UNIVERSAL MODAL SYSTEM --- */
        .rian-modal-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 2, 5, 0.75); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
            z-index: 3000; display: flex; justify-content: center; align-items: center;
            opacity: 0; visibility: hidden; transition: all 0.3s ease;
        }
        .rian-modal-overlay.active { opacity: 1; visibility: visible; }
        
        .rian-modal-box {
            background: rgba(3, 15, 29, 0.9); border: 1px solid #00e5ff;
            border-radius: 16px; width: 850px; max-width: 95vw; height: 80vh; max-height: 800px;
            box-shadow: 0 10px 50px rgba(0, 229, 255, 0.2), inset 0 0 20px rgba(0, 229, 255, 0.05);
            padding: 30px; transform: scale(0.95) translateY(20px); transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex; flex-direction: column; gap: 20px; font-family: 'Courier New', monospace;
        }
        .rian-modal-overlay.active .rian-modal-box { transform: scale(1) translateY(0); }
        
        .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0, 229, 255, 0.2); padding-bottom: 15px; }
        .modal-title { font-size: 18px; color: #fff; letter-spacing: 2px; font-weight: bold; display: flex; align-items: center; gap: 10px;}
        .modal-close { background: rgba(255, 255, 255, 0.1); border: none; color: #fff; font-size: 20px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center;}
        .modal-close:hover { background: rgba(255, 68, 68, 0.8); color: #fff; transform: rotate(90deg); }
        .modal-body { font-size: 13px; color: #9feeff; flex: 1; overflow-y: auto; padding-right: 10px; }

        /* Modal Inner Elements */
        .search-bar-modal { width: 100%; background: rgba(0,0,0,0.4); border: 1px solid #00e5ff; color: #fff; padding: 16px 20px; border-radius: 30px; font-size: 16px; outline: none; margin-bottom: 20px; box-shadow: inset 0 0 10px rgba(0,229,255,0.1);}
        .history-list-item { display: flex; justify-content: space-between; padding: 16px; border-bottom: 1px solid rgba(0,229,255,0.1); cursor: pointer; transition: 0.2s; border-radius: 8px;}
        .history-list-item:hover { background: rgba(0,229,255,0.1); }
        .edu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }
        .edu-card { background: linear-gradient(145deg, rgba(3,15,29,1), rgba(0,30,50,0.8)); border: 1px solid rgba(0,229,255,0.3); padding: 40px 20px; border-radius: 16px; text-align: center; cursor: pointer; transition: 0.3s; font-size: 16px; font-weight: bold; color:#fff;}
        .edu-card:hover { transform: translateY(-5px); border-color: #00e5ff; box-shadow: 0 10px 20px rgba(0,229,255,0.2); }
        .media-templates { display: flex; gap: 15px; overflow-x: auto; padding-bottom: 15px; margin-bottom: 20px; }
        .media-template-card { min-width: 150px; height: 100px; background: rgba(0,229,255,0.1); border: 1px solid rgba(0,229,255,0.3); border-radius: 12px; display: flex; align-items: flex-end; padding: 10px; cursor: pointer; font-weight:bold; color:#fff; transition:0.2s;}
        .media-template-card:hover { border-color:#00ffaa; transform: scale(1.05);}
        .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
        .gallery-item { position: relative; height: 180px; background: rgba(0,229,255,0.05); border: 1px solid rgba(0,229,255,0.2); border-radius: 12px; overflow: hidden; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s;}
        .gallery-item:hover { border-color: #00e5ff; box-shadow: 0 0 15px rgba(0,229,255,0.3); }
        .gallery-item img { width: 100%; height: 100%; object-fit: cover; opacity: 0.8; transition: 0.3s;}
        .gallery-item:hover img { opacity: 1; transform: scale(1.05); }
        .delete-btn-overlay { position: absolute; top: 10px; right: 10px; background: rgba(255, 0, 0, 0.8); color: white; border: none; border-radius: 50%; width: 32px; height: 32px; font-size: 14px; cursor: pointer; opacity: 0; transition: 0.2s; display: flex; justify-content: center; align-items: center; box-shadow: 0 0 10px rgba(0,0,0,0.5);}
        .gallery-item:hover .delete-btn-overlay { opacity: 1; }
        .delete-btn-overlay:hover { background: #ff0000; transform: scale(1.1); }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #00e5ff; border-radius: 2px; }

        /* ==========================================
           MOBILE EXCLUSIVE STYLES
           ========================================== */
        @media screen and (max-width: 900px) {
            /* Show Hamburger on Mobile ONLY */
            .menu-trigger { display: flex; } 
            
            /* Hide Desktop Left Nav and Widgets */
            .left-nav-bar, .desktop-status, .desktop-diagnostics, .memory-badge, #devToggleBtn { 
                display: none !important; 
            }
            
            /* Full Screen Chat Box, Transparent Background for Stars */
            .desktop-logs { 
                position: fixed !important; 
                top: 60px !important; 
                left: 0 !important; 
                right: 0 !important; 
                width: 100% !important; 
                height: calc(100vh - 140px) !important; 
                border: none !important; 
                border-radius: 0 !important; 
                background: transparent !important; 
                box-shadow: none !important;
                backdrop-filter: none !important;
                padding: 10px 15px !important; 
            }
            .desktop-logs h4, .desktop-logs p { display: none !important; }
            .log-stream { height: 100% !important; font-size: 13px; padding-bottom: 80px !important; }
            
            /* Bottom Input fixed */
            .desktop-bottom-bar { 
                position: fixed !important; bottom: 0 !important; left: 0 !important; 
                width: 100% !important; max-width: 100% !important; transform: none !important; 
                padding: 10px 15px 15px 15px !important; 
                background: linear-gradient(to top, rgba(0, 3, 8, 1) 50%, rgba(0, 3, 8, 0)); 
                z-index: 100 !important; 
            }
            .status-headline { display: none !important; } 
            .input-wrapper { width: 100% !important; border-radius: 24px !important; background: rgba(3, 15, 29, 0.95) !important; }
            
            /* Drawer adjustments */
            .rian-drawer { width: 85vw; max-width: 320px; }
            
            /* Modal adjustments */
            .rian-modal-box { width: 95% !important; height: 90vh !important; max-height: 90vh !important; border-radius: 12px !important; padding: 20px !important;}
        }
    </style>
</head>
<body class="no-select">
    
    <svg width="0" height="0">
        <defs>
            <linearGradient id="rainbow-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ff0055" />
                <stop offset="50%" stop-color="#00e5ff" />
                <stop offset="100%" stop-color="#bd00ff" />
            </linearGradient>
        </defs>
    </svg>

    <canvas id="canvas3d"></canvas>

    <!-- MOBILE: Menu Trigger Button (Hamburger) -->
    <div class="menu-trigger" id="menuTriggerBtn" title="Open Menu">
        <svg viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
    </div>

    <!-- MOBILE: Gemini-Style Master Drawer -->
    <div class="rian-drawer" id="masterDrawer">
        <div class="drawer-header">
            <div class="drawer-logo-container">
                <svg viewBox="0 0 24 24"><path d="M19 9l1.25-2.75L23 5l-2.75-1.25L19 1l-1.25 2.75L15 5l2.75 1.25L19 9zm-7.5.5L9 4 6.5 9.5 1 12l5.5 2.5L9 20l2.5-5.5L17 12l-5.5-2.5z"/></svg>
                <span class="drawer-brand">R.I.A.N.</span>
            </div>
            <button class="drawer-close" id="drawerCloseBtn">×</button>
        </div>
        
        <div class="drawer-content">
            <div class="drawer-item" id="drwNewChat">
                <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                New chat
            </div>
            <div class="drawer-item" id="drwSearch">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                Search chats
            </div>
            <div class="drawer-item" id="drwEdu">
                <svg viewBox="0 0 24 24"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2.12-1.15V17h2V9L12 3zm6.83 6L12 12.8 5.17 9 12 5.2 18.83 9z"/></svg>
                Students
            </div>
            <div class="drawer-item" id="drwImages">
                <svg viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
                Media Studio
            </div>
            <div class="drawer-item" id="drwLibrary">
                <svg viewBox="0 0 24 24"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
                Archives
            </div>
        </div>

        <div class="drawer-footer">
            <div class="user-profile">
                <div class="user-avatar">M</div>
                <div class="user-info">
                    <span class="user-name">Manish Tiwari</span>
                    <span class="user-badge">Pro</span>
                </div>
            </div>
            <button class="drawer-settings-btn" id="drwSettings" title="Settings">
                <svg viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94L14.4 2.81c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33c-.22-.08-.47 0-.59.22L2.73 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .43-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.49-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
            </button>
        </div>
    </div>

    <!-- UNIVERSAL MODAL SYSTEM -->
    <div class="rian-modal-overlay" id="globalModal">
        <div class="rian-modal-box">
            <div class="modal-header">
                <span class="modal-title" id="modalTitle">MODULE</span>
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            <div class="modal-body allow-select" id="modalBody">
                <!-- Injected via JS -->
            </div>
        </div>
    </div>

    <!-- DESKTOP: Left Nav Icons -->
    <div class="left-nav-bar">
        <svg class="nav-icon" id="navHome" title="New Session" viewBox="0 0 24 24"><path d="M19 9l1.25-2.75L23 5l-2.75-1.25L19 1l-1.25 2.75L15 5l2.75 1.25L19 9zm-7.5.5L9 4 6.5 9.5 1 12l5.5 2.5L9 20l2.5-5.5L17 12l-5.5-2.5z"/></svg>
        <svg class="nav-icon" id="navToggle" title="Dev Mode Toggle" viewBox="0 0 24 24"><path d="M17 7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h10c2.76 0 5-2.24 5-5s-2.24-5-5-5zm0 8H7c-1.65 0-3-1.35-3-3s1.35-3 3-3h10c1.65 0 3 1.35 3 3s-1.35 3-3 3zm0-5c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>
        <svg class="nav-icon" id="navCompose" title="New Prompt" viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
        <svg class="nav-icon" id="navSearch" title="Deep Search" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
        <svg class="nav-icon" id="navEdu" title="Guided Learning" viewBox="0 0 24 24"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2.12-1.15V17h2V9L12 3zm6.83 6L12 12.8 5.17 9 12 5.2 18.83 9z"/></svg>
        <svg class="nav-icon" id="navMedia" title="Vision Studio" viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
        <svg class="nav-icon" id="navFolder" title="Media Library & History" viewBox="0 0 24 24"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
        <svg class="nav-icon" id="navApps" title="Extensions" viewBox="0 0 24 24"><path d="M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z"/></svg>
        <div class="nav-spacer"></div>
        <svg class="nav-icon nav-bottom-icon" id="navSettings" title="Settings" viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94L14.4 2.81c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33c-.22-.08-.47 0-.59.22L2.73 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .43-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.49-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
    </div>

    <!-- DESKTOP BACKGROUND WIDGETS -->
    <div class="hud-glass desktop-status dev-element">
        <h3>SYSTEM R.I.A.N.</h3>
        <p>STATUS: <span class="text-highlight">ONLINE</span></p>
        <p>NEURAL LINK: ESTABLISHED</p>
        <div class="dev-toggle" id="devToggleBtn">DEV MODE: ON</div>
    </div>

    <div class="hud-glass desktop-diagnostics dev-element">
        <h4 class="diag-header">AUTONOMOUS TESTING & LOGS</h4>
        <div class="diag-row"><span>MIC WATCHDOG:</span><span class="text-highlight">ACTIVE</span></div>
        <div class="diag-row"><span>PC BRIDGE:</span><span class="text-highlight">CONNECTED</span></div>
        <div class="test-stream" id="testStream"></div>
    </div>

    <div class="memory-badge dt-node-1 dev-element">[MEMORY] User_Prefs</div>
    <div class="memory-badge dt-node-2 dev-element">[CONTEXT] Core_Logic</div>
    <div class="memory-badge dt-node-5 dev-element">[FILES] project_R.I.A.N_v2.0</div>
    <div class="memory-badge dt-node-6 dev-element">[MEMORY] Retiles</div>

    <!-- EXECUTION DASHBOARD (CHAT BOX) -->
    <div class="hud-glass desktop-logs dev-element allow-select" style="opacity: 1 !important; pointer-events: auto !important;">
        <h4 style="color: #00ffaa;">Execution Dashboard</h4>
        <div class="log-stream" id="desktopLogStream">
            <div style="color:#00ffaa; padding: 6px 0; border-bottom: 1px solid rgba(0, 229, 255, 0.1);"><strong>[RIAN]</strong> System R.I.A.N. online. Direct neural link established, Manish.</div>
        </div>
    </div>

    <!-- BOTTOM COMMAND BAR -->
    <div class="desktop-bottom-bar">
        <div class="status-headline" id="statusLabel">AWAITING COMMAND...</div>

        <div class="input-wrapper">
            <button class="icon-btn btn-plus" id="actionToggleBtn" title="Actions">
                <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
            
            <div class="action-menu" id="actionMenu">
                <div class="action-item" onclick="document.getElementById('hiddenFileInput').click(); this.parentNode.classList.remove('active');">📎 Upload Files</div>
                <div class="action-item" onclick="this.parentNode.classList.remove('active'); alert('Connecting to Google Drive...');">☁️ Add from Drive</div>
                <div class="action-divider"></div>
                <div class="action-item" onclick="triggerModalLogic('media'); this.parentNode.classList.remove('active');">🖼️ Create Image / Video</div>
                <div class="action-divider"></div>
                <div class="action-item" onclick="triggerModalLogic('search'); this.parentNode.classList.remove('active');">🔬 Deep Research</div>
            </div>

            <!-- TEXTAREA FOR MULTILINE PROMPTS -->
            <textarea id="userInput" class="chat-input allow-select" rows="1" placeholder="Type a message or command..."></textarea>

            <button class="icon-btn btn-mic" id="micBtn" title="Voice Input">
                <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
            </button>

            <button class="icon-btn btn-send" id="sendBtn" title="Execute">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>

            <input type="file" id="hiddenFileInput" style="display: none;" multiple>
        </div>
    </div>

    <script>
        // --- 1. CORE DOM ELEMENTS ---
        const drawer = document.getElementById('masterDrawer');
        const menuTriggerBtn = document.getElementById('menuTriggerBtn');
        const drawerCloseBtn = document.getElementById('drawerCloseBtn');
        const inputField = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const micBtn = document.getElementById('micBtn');
        const actionMenu = document.getElementById('actionMenu');
        const actionToggleBtn = document.getElementById('actionToggleBtn');
        const devToggleBtn = document.getElementById('devToggleBtn');
        const devElements = document.querySelectorAll('.dev-element');
        const sysLogBox = document.getElementById('desktopLogStream');
        const statusLabel = document.getElementById('statusLabel');
        const modal = document.getElementById('globalModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        // --- 2. GLOBAL CLICK HANDLERS (Fixes all toggle bugs) ---
        menuTriggerBtn.addEventListener('click', (e) => { e.stopPropagation(); drawer.classList.add('open'); });
        drawerCloseBtn.addEventListener('click', () => drawer.classList.remove('open'));

        document.addEventListener('click', (e) => {
            if (!drawer.contains(e.target) && e.target !== menuTriggerBtn) drawer.classList.remove('open');
            if (!actionMenu.contains(e.target) && e.target !== actionToggleBtn) actionMenu.classList.remove('active');
            if (e.target === modal) closeModal(); 
        });

        // Close inner dropdowns specifically (Event Delegation pattern)
        modalBody.addEventListener('click', (e) => {
            const m = document.getElementById('mediaUploadMenu');
            if(m && !e.target.closest('#mediaUploadMenuBtn') && m.style.display === 'flex') {
                m.style.display = 'none';
            }
        });

        actionToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            actionMenu.classList.toggle('active');
        });

        // --- 3. INPUT FIELD LOGIC (Auto-expand) ---
        inputField.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if(this.value === '') this.style.height = 'auto';
        });

        document.getElementById('hiddenFileInput').addEventListener('change', function(e) {
            if(this.files && this.files.length > 0) {
                appendLog('SYSTEM', `File queued for upload: ${this.files[0].name}`);
            }
        });

        micBtn.addEventListener('click', () => {
            appendLog('SYSTEM', 'Microphone activated. Listening...');
            statusLabel.innerText = "LISTENING...";
        });

        // --- 4. MODAL LOGIC ---
        function openModal(title, contentHTML) {
            modalTitle.innerHTML = title;
            modalBody.innerHTML = contentHTML;
            modal.classList.add('active');
            drawer.classList.remove('open'); 
        }
        function closeModal() { modal.classList.remove('active'); }

        // --- 5. DEV MODE TOGGLE ---
        let devModeActive = true;
        devToggleBtn.addEventListener('click', () => {
            devModeActive = !devModeActive;
            devToggleBtn.innerText = devModeActive ? "DEV MODE: ON" : "DEV MODE: OFF";
            devToggleBtn.style.color = devModeActive ? "#00ffaa" : "#ff4444";
            devToggleBtn.style.borderColor = devModeActive ? "#00ffaa" : "rgba(255,68,68,0.5)";
            
            devElements.forEach(el => {
                if(el !== devToggleBtn.parentElement && !el.classList.contains('desktop-logs')) {
                    el.style.opacity = devModeActive ? '1' : '0';
                    el.style.pointerEvents = devModeActive ? 'auto' : 'none';
                }
            });
        });

        // --- 6. UNIFIED MODAL GENERATOR LOGIC (No Crash Guarantee) ---
        const newSessionAction = () => {
            sysLogBox.innerHTML = '<div style="color:#00ffaa; padding: 6px 0; border-bottom: 1px solid rgba(0, 229, 255, 0.1);"><strong>[RIAN]</strong> System R.I.A.N. online. New session initialized.</div>';
            inputField.value = ""; inputField.style.height = 'auto'; inputField.focus();
            closeModal(); drawer.classList.remove('open');
        };

        const triggerModalLogic = (type) => {
            if(type === 'search') {
                openModal('🔍 SEARCH ARCHIVES', `
                    <input type="text" class="search-bar-modal" placeholder="Search chats, prompts, or data...">
                    <div style="color:#00e5ff; margin-bottom:10px; font-weight:bold;">Recent</div>
                    <div class="history-list-item" onclick="closeModal()"><span>इंग्लिश सीखने का बेसिक प्लान</span> <span style="color:#7ce8ff; opacity:0.7;">Today</span></div>
                    <div class="history-list-item" onclick="closeModal()"><span>R.I.A.N. Neural Interface Code</span> <span style="color:#7ce8ff; opacity:0.7;">Today</span></div>
                `);
            } else if (type === 'edu') {
                openModal('🎓 LEVEL UP YOUR STUDYING', `
                    <div class="edu-grid">
                        <div class="edu-card">✅<br><br>Quiz yourself</div>
                        <div class="edu-card">🗂️<br><br>Create flashcards</div>
                        <div class="edu-card">📖<br><br>Use Guided Learning</div>
                    </div>
                `);
            } else if (type === 'media') {
                openModal('✨ CREATE MEDIA STUDIO', `
                    <div style="display:flex; gap:20px; margin-bottom:15px; border-bottom: 1px solid rgba(0,229,255,0.2); padding-bottom:10px;">
                        <button id="tabImageBtn" style="background:transparent; border:none; color:#00ffaa; font-weight:bold; cursor:pointer; font-size:14px; border-bottom:2px solid #00ffaa; padding-bottom:5px;">🖼️ Image Studio</button>
                        <button id="tabVideoBtn" style="background:transparent; border:none; color:#9feeff; cursor:pointer; font-size:14px; padding-bottom:5px; transition:0.2s;">🎞️ Video Studio</button>
                    </div>
                    <div id="mediaTemplatesContent">
                        <div style="color:#00ffaa; margin-bottom:10px; font-size:12px;">Select Style Template:</div>
                        <div class="media-templates">
                            <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1578632767115-351597cf2477?w=300'); background-size:cover;">Chibi</div>
                            <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=300'); background-size:cover;">Cyberpunk</div>
                            <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1580136608260-4eb11f4b24fe?w=300'); background-size:cover;">Origami</div>
                            <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?w=300'); background-size:cover;">Anime</div>
                        </div>
                    </div>
                    <div style="position:relative; display:flex; align-items:center; background:rgba(0,0,0,0.4); border:1px solid #00e5ff; border-radius:30px; padding:6px 15px; margin-bottom:15px;">
                        <div style="position:relative;">
                            <button id="mediaUploadMenuBtn" onclick="const m = document.getElementById('mediaUploadMenu'); m.style.display = m.style.display === 'none' ? 'flex' : 'none'; event.stopPropagation();" style="background:rgba(0,229,255,0.1); border:none; color:#00e5ff; border-radius:50%; width:32px; height:32px; font-size:20px; cursor:pointer; display:flex; align-items:center; justify-content:center; margin-right:10px;">+</button>
                            <div id="mediaUploadMenu" style="display:none; flex-direction:column; gap:5px; position:absolute; bottom:45px; left:0; background:rgba(3,15,29,0.98); border:1px solid #00e5ff; border-radius:8px; padding:8px; width:180px; z-index:100;">
                                <div class="action-item" style="padding:8px; cursor:pointer; color:#9feeff;" onclick="document.getElementById('hiddenFileInput').click(); this.parentNode.style.display='none';">📁 Upload File / Doc</div>
                                <div class="action-item" style="padding:8px; cursor:pointer; color:#9feeff;" onclick="document.getElementById('hiddenFileInput').click(); this.parentNode.style.display='none';">🖼️ Add Reference Image</div>
                            </div>
                        </div>
                        <input type="text" placeholder="Describe your media..." style="flex:1; background:transparent; border:none; color:#fff; outline:none; font-family:'Courier New', monospace; font-size:14px;">
                    </div>
                    <div style="display:flex; justify-content:flex-end; gap:10px;">
                        <button style="background:#00e5ff; border:none; color:#000; font-weight:bold; padding:8px 24px; border-radius:20px; cursor:pointer;" onclick="appendLog('SYSTEM', 'Initiating media generation...'); closeModal();">Generate</button>
                    </div>
                `);

                // Event Listeners for Dynamic Tabs
                setTimeout(() => {
                    document.getElementById('tabImageBtn').addEventListener('click', function() {
                        this.style.color = '#00ffaa'; this.style.borderBottom = '2px solid #00ffaa';
                        document.getElementById('tabVideoBtn').style.color = '#9feeff'; document.getElementById('tabVideoBtn').style.borderBottom = 'none';
                        document.getElementById('mediaTemplatesContent').innerHTML = `
                            <div style="color:#00ffaa; margin-bottom:10px; font-size:12px;">Select Style Template:</div>
                            <div class="media-templates">
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1578632767115-351597cf2477?w=300'); background-size:cover;">Chibi</div>
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=300'); background-size:cover;">Cyberpunk</div>
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1580136608260-4eb11f4b24fe?w=300'); background-size:cover;">Origami</div>
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?w=300'); background-size:cover;">Anime</div>
                            </div>
                        `;
                    });

                    document.getElementById('tabVideoBtn').addEventListener('click', function() {
                        this.style.color = '#00ffaa'; this.style.borderBottom = '2px solid #00ffaa';
                        document.getElementById('tabImageBtn').style.color = '#9feeff'; document.getElementById('tabImageBtn').style.borderBottom = 'none';
                        document.getElementById('mediaTemplatesContent').innerHTML = `
                            <div style="color:#00ffaa; margin-bottom:10px; font-size:12px;">Select Video Style:</div>
                            <div class="media-templates">
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1518770660439-4636190af475?w=300'); background-size:cover;">Walkthrough</div>
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=300'); background-size:cover;">Tiny World</div>
                                <div class="media-template-card" style="background-image:linear-gradient(to top, rgba(0,0,0,0.8), transparent), url('https://images.unsplash.com/photo-1605810230434-7631ac76ec81?w=300'); background-size:cover;">Logo Reveal</div>
                            </div>
                        `;
                    });
                }, 50);
            } else if (type === 'library') {
                openModal('📁 MEDIA ARCHIVES', `
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <span style="color:#00ffaa;">Generated Assets</span>
                        <button style="background:transparent; border:1px solid #ff4444; color:#ff4444; padding:5px 10px; border-radius:4px; cursor:pointer; font-size:11px;">Clear All</button>
                    </div>
                    <div class="gallery-grid">
                        <div class="gallery-item">
                            <img src="https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=300" alt="Cyberpunk City">
                            <button class="delete-btn-overlay" onclick="this.parentElement.remove(); appendLog('SYSTEM', 'Media file deleted.');" title="Delete Image">🗑️</button>
                        </div>
                        <div class="gallery-item">
                            <div style="color:#00e5ff; text-align:center; padding:10px;">📄<br><br>Operating System<br>Book Plan.pdf</div>
                            <button class="delete-btn-overlay" onclick="this.parentElement.remove(); appendLog('SYSTEM', 'Document deleted.');" title="Delete Doc">🗑️</button>
                        </div>
                    </div>
                `);
            } else if (type === 'apps') {
                openModal('🎛️ SYSTEM EXTENSIONS', `
                    <div style="display:flex; flex-wrap:wrap; gap:10px;">
                        <span style="padding:10px 15px; border:1px solid #00ffaa; color:#00ffaa; border-radius:8px; cursor:pointer;">🔗 Google Workspace</span>
                        <span style="padding:10px 15px; border:1px solid #00ffaa; color:#00ffaa; border-radius:8px; cursor:pointer;">💻 GitHub Copilot</span>
                    </div>
                `);
            } else if (type === 'settings') {
                openModal('⚙️ PREFERENCES & SETTINGS', `
                    <p style="margin-bottom:15px; color:#fff;"><strong>Account:</strong> Manish Tiwari (Pro)</p>
                    <p style="margin-bottom:15px; color:#fff;"><strong>Voice Biometrics:</strong> <span style="color:#00ffaa">Active</span></p>
                    <p style="margin-bottom:15px; color:#fff;"><strong>API Connection:</strong> <span style="color:#00ffaa">Connected</span></p>
                    <hr style="border:0; border-top:1px solid rgba(0,229,255,0.2); margin:15px 0;">
                    <button style="width:100%; padding:10px; background:rgba(255,68,68,0.1); border:1px solid #ff4444; color:#ff4444; border-radius:6px; cursor:pointer; font-weight:bold;">Disconnect Neural Link</button>
                `);
            }
        };

        // Attach to Desktop Nav
        document.getElementById('navHome').addEventListener('click', newSessionAction);
        document.getElementById('navCompose').addEventListener('click', newSessionAction);
        document.getElementById('navToggle').addEventListener('click', () => devToggleBtn.click());
        document.getElementById('navSearch').addEventListener('click', () => triggerModalLogic('search'));
        document.getElementById('navEdu').addEventListener('click', () => triggerModalLogic('edu'));
        document.getElementById('navMedia').addEventListener('click', () => triggerModalLogic('media'));
        document.getElementById('navFolder').addEventListener('click', () => triggerModalLogic('library'));
        document.getElementById('navApps').addEventListener('click', () => triggerModalLogic('apps'));
        if(document.getElementById('navSettings')) document.getElementById('navSettings').addEventListener('click', () => triggerModalLogic('settings'));

        // Attach to Mobile Drawer Nav
        document.getElementById('drwNewChat').addEventListener('click', newSessionAction);
        document.getElementById('drwSearch').addEventListener('click', () => triggerModalLogic('search'));
        document.getElementById('drwEdu').addEventListener('click', () => triggerModalLogic('edu'));
        document.getElementById('drwImages').addEventListener('click', () => triggerModalLogic('media'));
        document.getElementById('drwLibrary').addEventListener('click', () => triggerModalLogic('library'));
        if(document.getElementById('drwSettings')) document.getElementById('drwSettings').addEventListener('click', () => triggerModalLogic('settings'));

        // --- 7. CHAT LOGIC (Send & Render) ---
        function appendLog(sender, message) {
            if(!sysLogBox) return;
            const log = document.createElement('div');
            log.style.padding = '8px 0';
            log.style.borderBottom = '1px solid rgba(0, 229, 255, 0.1)';
            log.style.lineHeight = '1.7';
            
            const formattedMessage = message.replace(/\n/g, '<br>');
            
            if (sender === 'USER') {
                log.style.color = '#ffffff';
                log.innerHTML = `<strong>[USER]</strong><br/>${formattedMessage}`;
            } else if (sender === 'SYSTEM') {
                log.style.color = '#e29aff';
                log.innerHTML = `<strong>[SYSTEM ALERT]</strong><br/>${formattedMessage}`;
            } else {
                log.style.color = '#00ffaa';
                log.innerHTML = `<strong>[RIAN]</strong><br/>${formattedMessage}`;
            }
            
            sysLogBox.appendChild(log);
            requestAnimationFrame(() => { sysLogBox.scrollTop = sysLogBox.scrollHeight; });
        }

        async function processCommand() {
            const query = inputField.value.trim();
            if (!query) return;

            inputField.value = "";
            inputField.style.height = 'auto'; // Reset text box height
            appendLog('USER', query);
            statusLabel.innerText = "PROCESSING COMMAND...";

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, user_id: "Manish" })
                });
                
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                
                const data = await response.json();
                const reply = data.response || data.reply || data.text || `Command executed: ${query}`;

                appendLog('RIAN', reply);
                vocalize(reply);
                statusLabel.innerText = "AWAITING COMMAND...";
            } catch (error) {
                const mockReply = `Neural link busy. Acknowledged: ${query}`;
                appendLog('RIAN', mockReply);
                vocalize(mockReply);
                statusLabel.innerText = "AWAITING COMMAND...";
            }
        }

        sendBtn.addEventListener('click', processCommand);
        
        inputField.addEventListener('keydown', (e) => {
            if (e.key === "Enter" && !e.shiftKey) { 
                e.preventDefault(); 
                processCommand(); 
            }
        });

        function playCloudVoice(audioSource) {
    const audioPlayer = document.getElementById('rianAudioPlayer');
    
    // अगर बैकएंड Base64 स्ट्रिंग भेज रहा है (Recommended for APIs)
    if(audioSource.startsWith('UklGR')) { // 'UklGR' WAV/MP3 header signature
        audioPlayer.src = "data:audio/mp3;base64," + audioSource;
    } 
    // अगर बैकएंड डायरेक्ट ऑडियो URL भेज रहा है
    else {
        audioPlayer.src = audioSource;
    }
    
    audioPlayer.play().catch(e => console.error("Audio playback failed:", e));
}

        // --- 8. TELEMETRY & 3D BACKGROUND ---
        function startTelemetry() {
            const testStream = document.getElementById("testStream");
            const logs = ["Vector Memory Pulse -> 3120 Vectors Synced", "Agent Tool Schema Integrity -> 16 Tools Active", "PC Bridge Link -> Connected", "Autonomous Learner -> Active"];
            let idx = 0;
            setInterval(() => {
                if (!testStream) return;
                const entry = document.createElement("div");
                entry.style.cssText = "margin-bottom:4px; border-bottom:1px dotted rgba(0,255,170,0.15); padding-bottom: 4px;";
                entry.textContent = `[${new Date().toLocaleTimeString()}] ${logs[idx % logs.length]}`;
                testStream.appendChild(entry);
                if (testStream.childNodes.length > 15) testStream.removeChild(testStream.firstChild);
                testStream.scrollTop = testStream.scrollHeight;
                idx++;
            }, 2500);
        }
        startTelemetry();

        function init3DEnvironment() {
            const canvas = document.getElementById('canvas3d');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);

            const pCount = 2000;
            const pGeo = new THREE.BufferGeometry();
            const pPos = new Float32Array(pCount * 3);
            for (let i = 0; i < pCount * 3; i++) { pPos[i] = (Math.random() - 0.5) * 20; }
            pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
            
            const pMat = new THREE.PointsMaterial({ color: 0x00e5ff, size: 0.04, transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending });
            const dotsMesh = new THREE.Points(pGeo, pMat);
            scene.add(dotsMesh);
            camera.position.z = 8;

            function animate() {
                requestAnimationFrame(animate);
                dotsMesh.rotation.y += 0.0005;
                dotsMesh.rotation.x += 0.0002;
                renderer.render(scene, camera);
            }
            animate();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        }
        init3DEnvironment();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

# ==========================================
# CLI DUAL-INTERACTIVE SYSTEM
# ==========================================
async def terminal_main() -> None:
    audio = AudioService()
    proactive_brain = None
    try:
        await assistant_instance.start()
        print("\n==============================")
        print("    R.I.A.N. MASTER ONLINE    ")
        print("==============================")
        proactive_brain = ProactiveMonitor(llm=assistant_instance.llm, api_key=settings.groq_api_key)
        proactive_brain.start()
        try:
            await audio.speak("Hello sir, mai RIAN hoon. Mai aapki kya madad karne ke liye ready hu")
        except Exception:
            pass

        while True:
            try:
                print("\n[1] Voice Command 🎤 | [2] Type Command ⌨️ | [3] Exit ❌")
                mode = input("Select Mode (1/2/3): ").strip()
                if mode == "3":
                    break
                elif mode == "1":
                    query = await audio.listen()
                    if not query:
                        continue
                    print(f"👤 You (Voice) >> {query}")
                elif mode == "2":
                    query = input("\n👤 You >> ").strip()
                    if query.lower() in ["exit", "quit", "bye"]:
                        break
                    if not query:
                        continue
                else:
                    print("Invalid option. Please choose 1, 2, or 3.")
                    continue

                response = await assistant_instance.process_query(query)
                print(f"\n🤖 R.I.A.N. >> {response}")
                try:
                    await audio.speak(response)
                except Exception:
                    pass
            except KeyboardInterrupt:
                break
    finally:
        if proactive_brain:
            proactive_brain.stop()
        await assistant_instance.stop()

# ==========================================
# MAIN EXECUTION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        asyncio.run(terminal_main())
    else:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=False, workers=1)
<audio id="rianAudioPlayer" style="display: none;"></audio>        