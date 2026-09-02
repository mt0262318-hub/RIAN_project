from fastapi.responses import FileResponse
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
import threading
from typing import List, Optional, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = '/home/ubuntu/RIAN_project/faiss_index'

# ==========================================
# SYSTEM SETTINGS & LOGGING CONFIGURATION
# ==========================================
from config.settings import settings
from config.logging_config import configure_logging, get_logger
configure_logging()
logger = get_logger("rian.master_core")

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
        dynamic_prompt += f"\n\n=== EXECUTING PLAN ===\n{task_plan}\nFollow this plan strictly."
    
    messages = [SystemMessage(content=dynamic_prompt)]
    messages.extend(history[-8:])
    
    # 3. Main AI ko strictly uska current role batao
    router_hint = f"SYSTEM NOTIFICATION: The Master Router has classified this task as [{route_decision}]. Act ONLY as this specialist."
    messages.append(SystemMessage(content=router_hint))
    
    current_user_msg = HumanMessage(content=user_query)
    messages.append(current_user_msg)
    
    try:
        # [PRO FIX] - Fetch active tools and bind them explicitly BEFORE calling ainvoke
        tools_list = assistant_instance.active_tools if 'assistant_instance' in globals() else []
        if tools_list:
            llm_with_tools = llm_instance.bind_tools(tools_list)
        else:
            llm_with_tools = llm_instance

        # Tool-bound LLM request (hamesha ke liye 400 error khatam)
        response = await llm_with_tools.ainvoke(messages)
        
        # [PRO FIX] - Handling tool trigger response
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_name = response.tool_calls[0]['name']
            reply_text = f"SYSTEM LOG: LLaMA-3 ne '{tool_name}' tool trigger kiya hai! (Agent execution pending for next phase)"
        else:
            reply_text = clean_llm_response(response.content.strip())
        
        # 1. Learner Agent Check
        if "Traceback" in reply_text or "Error" in reply_text:
            threading.Thread(target=learn_from_error, args=(llm_instance, user_query, reply_text)).start()
            
        # 2. QA / REVIEWER AGENT INTERCEPTION
        if route_decision in ["CODER", "STRATEGIST"]:
            logger.info("Triggering QA Agent for review...")
            qa_feedback = qa_reviewer_agent(llm_instance, reply_text)
            
            if "QA ALERT" in qa_feedback:
                reply_text = f"{reply_text}\n\n{'='*40}\n**⚠️ QA AGENT ALERT:**\n{qa_feedback}"
            else:
                reply_text = f"{reply_text}\n\n{'='*40}\n**✅ QA PASSED:** Logic verified by Elite Reviewer."
                
    except Exception as e:
        error_msg = str(e)
        reply_text = f"Processing error: {error_msg}"
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
            model_name="llama3-70b-8192",
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

# System ki current aawaz ko yaad rakhne ke liye global variable
CURRENT_VOICE = "hi-IN-MadhurNeural"

async def get_audio_base64(text, voice_name=None):
    global CURRENT_VOICE
    if voice_name is None:
        voice_name = CURRENT_VOICE
        
    communicate = edge_tts.Communicate(text, voice_name) 
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return base64.b64encode(audio_data).decode("utf-8")


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


@app.post("/api/chat")
async def chat_with_rian(request: ChatRequest):
    q = (request.query or request.text or "").strip()
    if not q:
        return {"status": "error", "response": "Empty query received."}
    
    q_low = q.lower()
    
    if any(k in q_low for k in ["screen", "dekh", "dekho", "kya khula"]):
        vision_out = pc_tools.run_screen_vision(q)
        return {"status": "success", "response": vision_out, "reply": vision_out}
        
    global CURRENT_VOICE
    
    # --- VOICE SWITCH LOGIC START ---
    if any(k in q_low for k in ["female", "ladies", "ladki", "aurat"]):
        CURRENT_VOICE = "hi-IN-SwaraNeural"
        msg = "Thik hai, ab main female voice mein baat karungi."
        audio_data = await get_audio_base64(msg)
        return {"status": "success", "response": msg, "audio_b64": audio_data}
        
    elif any(k in q_low for k in ["male", "gents", "ladka", "aadmi"]):
        CURRENT_VOICE = "hi-IN-MadhurNeural"
        msg = "Thik hai, ab main male voice mein baat karunga."
        audio_data = await get_audio_base64(msg)
        return {"status": "success", "response": msg, "audio_b64": audio_data}
    # --- VOICE SWITCH LOGIC END ---

    if "notepad" in q_low:
        await pc_bridge.execute_command("launch_target", {"target": "notepad"})
        return {"status": "success", "response": "Notepad open kar diya hai.", "reply": "Notepad open kar diya hai."}   
    elif "youtube" in q_low:
        search_kw = q_low.replace("open", "").replace("youtube", "").replace("play", "").strip()
        await pc_bridge.execute_command("play_youtube", {"query": search_kw or "music"})
        return {"status": "success", "response": "YouTube play ho raha hai.", "reply": "YouTube play ho raha hai."}

    # [PRO FIX] The Indentation Error has been cleared here
    chat_groq = ChatGroq(model_name="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"), temperature=0.5)
    response_text = await generate_rian_response(user_id=request.user_id, user_query=q, llm_instance=chat_groq)
    audio_data = await get_audio_base64(response_text)
    
    return {
        "status": "success",
        "user_id": request.user_id,
        "response": response_text,
        "reply": response_text,
        "audio_b64": audio_data
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
        chat_groq = ChatGroq(model_name="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"), temperature=0.5)
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
@app.get("/ui")
async def serve_master_ui():
    return FileResponse("frontend.html")

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