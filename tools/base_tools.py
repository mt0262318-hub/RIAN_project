import os
import sys

# Headless Linux Safe Mock for GUI Tools
class MockPyAutoGUI:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

sys.modules['pyautogui'] = MockPyAutoGUI()
sys.modules['mouseinfo'] = MockPyAutoGUI()

from tools.skill_creator import create_new_skill
import importlib.util
import os
import logging
import webbrowser
#import pyautogui
import importlib.util
import inspect
from langchain_core.tools import BaseTool
from langchain_core.tools import tool
from memory.manager import MemoryManager

logger = logging.getLogger("rian.tools")
memory_manager = MemoryManager()

@tool
def search_google(query: str) -> str:
    """Search something on Google"""
    try:
        search_url = f"https://www.google.com/search?q={query}"
        print("[Cloud Mode] Browser popup suppressed.")
        return f"Searching '{query}' on Google"
    except Exception as e:
        logger.error(f"Google search failed: {e}")
        return f"Search failed: {e}"

@tool
def create_new_skill(tool_name: str, description: str, python_code: str) -> str:
    """Creates a new Python tool/skill for R.I.A.N. after getting human approval. 
    Use this when the user asks you to learn something new."""
    
    print(f"\n\n🚨 [SECURITY ALERT] R.I.A.N. wants to write a new skill: {tool_name} 🚨")
    print(f"Description: {description}")
    print("--- GENERATED CODE ---")
    print(python_code)
    print("----------------------")
    
    # Rule 1: Human-in-the-Loop (Approval)
    approval = input(f"\nDo you allow R.I.A.N. to save this code to your PC? (Y/N): ").strip().upper()
    
    if approval != 'Y':
        logger.warning(f"User rejected skill creation: {tool_name}")
        return f"Access Denied: The user rejected the creation of the tool '{tool_name}'. Stop and apologize."
    
    # Rule 2: Sandbox Environment 
    sandbox_dir = "custom_skills"
    if not os.path.exists(sandbox_dir):
        os.makedirs(sandbox_dir)
        
    # Sirf alphanumeric naam allow karenge taaki hack na ho
    safe_name = "".join([c for c in tool_name if c.isalnum() or c == "_"])
    file_path = os.path.join(sandbox_dir, f"{safe_name}.py")
    
    try:
        # 🚨 FIX: Raw string escapes (\n, \t) ko actual formatting mein convert karna
        clean_code = python_code.encode('utf-8').decode('unicode_escape')
        
        # Agar code ke aage-piche abhi bhi quotes bache ho toh unhe saaf karna
        if clean_code.startswith(('"', "'")) and clean_code.endswith(('"', "'")):
            clean_code = clean_code[1:-1]

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_code)
            
        return f"Success: Skill '{tool_name}' saved safely in {file_path}. Tell the user it was successful."
    except Exception as e:
        logger.error(f"Failed to write skill code: {e}")
        return f"Failed to create tool: {e}"

@tool
def open_website(website_name: str) -> str:
    """Open a known website or application like YouTube, Canva, etc."""
    try:
        url_map = {
            "youtube": "https://www.youtube.com",
            "canva": "https://www.canva.com",
            "google": "https://www.google.com",
            "chatgpt": "https://chat.openai.com",
            "github": "https://github.com"
        }
        
        name_lower = website_name.lower().strip()
        url = url_map.get(name_lower)
        
        if url:
            print("[Cloud Mode] Browser popup suppressed.")
            return f"Successfully opened {website_name}."
        else:
            # Agar direct link nahi hai, toh google search karke open karega
            search_url = f"https://www.google.com/search?q={website_name}"
            print("[Cloud Mode] Browser popup suppressed.")
            return f"Opened search results for {website_name}."
            
    except Exception as e:
        logger.error(f"Website opener failed: {e}")
        return f"Failed to open {website_name}: {e}"

@tool
def save_to_memory(text: str, metadata: dict = None) -> str:
    """Save information to R.I.A.N.'s memory"""
    try:
        doc_id = memory_manager.remember(text, metadata)
        return f"Memory saved successfully (ID: {doc_id})"
    except Exception as e:
        logger.error(f"Memory save failed: {e}")
        return f"Failed to save memory: {e}"

@tool
def recall_from_memory(query: str, k: int = 3) -> str:
    """Recall information from R.I.A.N.'s memory"""
    try:
        results = memory_manager.recall(query, k)
        if not results:
            return "No memories found for this query"
        return "\n".join(results)
    except Exception as e:
        logger.error(f"Memory recall failed: {e}")
        return f"Failed to recall memory: {e}"

@tool
def media_control(action: str) -> str:
    """Control media (play/pause)"""
    try:
        if action.lower() in ["play", "pause", "toggle"]:
            pyautogui.press("playpause")
            return f"Media {action}d successfully"
        return "Invalid action. Use: play, pause, or toggle"
    except Exception as e:
        logger.error(f"Media control failed: {e}")
        return f"Media control failed: {e}"

@tool
def get_memory_stats() -> str:
    """Get R.I.A.N.'s memory statistics"""
    try:
        stats = memory_manager.stats()
        return f"Memory Stats: {stats}"
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return f"Failed to get stats: {e}"

# Yahan saare tools sahi se map hone chahiye
ALL_TOOLS = [
    search_google,
    save_to_memory,
    recall_from_memory,
    media_control,
    get_memory_stats,
    open_website,
    create_new_skill  # <--- Naya Tool Yahan Add Kiya
]

def load_custom_tools(sandbox_dir="tools/custom_tools"):
    """Scans the custom_skills folder and dynamically loads any valid Langchain tools."""
    custom_tools = []
    if not os.path.exists(sandbox_dir):
        return custom_tools
        
    for filename in os.listdir(sandbox_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            file_path = os.path.join(sandbox_dir, filename)
            
            try:
                # File ko dynamically read karna
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # File ke andar jitne bhi @tool hain, unko nikalna
                for name, obj in inspect.getmembers(module):
                    if isinstance(obj, BaseTool):
                        custom_tools.append(obj)
                        logger.info(f"Loaded custom tool: {name} from {filename}")
            except Exception as e:
                logger.error(f"Failed to load custom tool from {filename}: {e}")
                
    return custom_tools
