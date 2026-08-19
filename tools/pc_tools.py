import os
import json
import asyncio
import logging
from langchain_core.tools import tool
from groq import Groq

logger = logging.getLogger("rian.pc_tools")
_bridge_instance = None

def set_bridge_instance(bridge):
    global _bridge_instance
    _bridge_instance = bridge

def execute_bridge_sync(action: str, params: dict) -> dict:
    if not _bridge_instance or not _bridge_instance.connected_pc:
        return {"status": "error", "message": "Laptop bridge connected nahi hai."}
    if not _bridge_instance.main_loop:
        return {"status": "error", "message": "Server event loop ready nahi hai."}
    
    future = asyncio.run_coroutine_threadsafe(
        _bridge_instance.execute_command(action, params),
        _bridge_instance.main_loop
    )
    try:
        return future.result(timeout=25)
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_screen_vision(question: str) -> str:
    res = execute_bridge_sync("inspect_screen", {})
    if res.get("status") != "success" or "image_b64" not in res:
        return f"Screen capture nahi ho saka: {res.get('message', 'No image data')}"
    
    b64_img = res["image_b64"]
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY cloud par configured nahi hai."
    
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are R.I.A.N. assistant. Look at the user's laptop screen and answer accurately in Hindi/Hinglish: {question}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        }
                    ]
                }
            ],
            temperature=0.2,
            max_tokens=600
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Vision Model Error: {e}"

@tool
def analyze_laptop_screen(user_question: str) -> str:
    """Capture and inspect the live laptop screen to answer questions, debug code, or describe open applications."""
    return run_screen_vision(user_question)

@tool
def play_youtube_video(query: str) -> str:
    """Directly play any song or video on YouTube in Chrome App mode."""
    res = execute_bridge_sync("play_youtube", {"query": query})
    return str(res.get("message", res))

@tool
def open_system_app_or_file(target: str) -> str:
    """Open any application, desktop shortcut, or file on the laptop."""
    res = execute_bridge_sync("launch_target", {"target": target})
    return str(res.get("message", res))

@tool
def control_pc_hardware(command: str) -> str:
    """Control physical PC hardware (mute, volume_up, volume_down, play_pause)."""
    res = execute_bridge_sync("system_control", {"command": command})
    return str(res.get("message", res))

@tool
def control_mouse(action: str, x: int = None, y: int = None, clicks: int = 1) -> str:
    """Control laptop mouse cursor and actions.
    action options: 'move', 'click', 'right_click', 'double_click', 'scroll_down', 'scroll_up', 'drag'
    x: Optional horizontal screen coordinate (pixel)
    y: Optional vertical screen coordinate (pixel)
    clicks: Number of clicks (default 1)
    """
    params = {
        "sub_action": action.lower(),
        "x": x,
        "y": y,
        "clicks": clicks
    }
    res = execute_bridge_sync("control_mouse", params)
    return str(res.get("message", res))

@tool
def scroll_screen(direction: str = "down", amount: int = 300) -> str:
    """Scroll the laptop screen up or down. direction: 'down' or 'up'."""
    sub_act = "scroll_down" if "down" in direction.lower() else "scroll_up"
    params = {
        "sub_action": sub_act,
        "amount": amount
    }
    res = execute_bridge_sync("control_mouse", params)
    return str(res.get("message", res))
@tool
def type_text_on_laptop(text: str) -> str:
    """Types text directly into the active window or input box on the laptop."""
    res = execute_bridge_sync("type_text", {"text": text})
    return str(res.get("message", res))


@tool
def trigger_hotkey_shortcut(keys: str) -> str:
    """Presses keyboard shortcuts on laptop. Pass comma-separated keys like 'ctrl,c', 'ctrl,v', 'alt,tab', 'enter', 'win'."""
    key_list = [k.strip() for k in keys.split(",")]
    res = execute_bridge_sync("hotkey", {"keys": key_list})
    return str(res.get("message", res))

@tool
def write_into_app(app_name: str, text: str) -> str:
    """Opens an application (like notepad, chrome, word) and automatically types the given text into it.
    Use this whenever user asks to open an app and write or type something in it.
    """
    res = execute_bridge_sync(
        "type_text", {"text": text, "app_name": app_name}
    )
    return str(res.get("message", res))