import logging
import pyautogui
from langchain_core.tools import tool

logger = logging.getLogger("rian.skills")

@tool
def control_volume(action: str) -> str:
    """Controls the master volume of the PC using keyboard key simulation. 
    Actions can be: 'mute', 'unmute', 'up', 'down', 'full'."""
    try:
        # PyAutoGUI ke fail-safe ko short delay par set karte hain taaki fast kaam kare
        pyautogui.PAUSE = 0.05
        
        if action == "mute":
            pyautogui.press("volumemute")
            return "PC Volume mute/unmute key pressed."
            
        elif action == "unmute":
            # Agar muted hai toh mute key dobara dabane se unmute ho jata hai Windows mein
            pyautogui.press("volumemute")
            return "PC Volume mute/unmute key pressed to unmute."
            
        elif action == "up":
            # Volume up key ko 5 baar dabayenge taaki significant change dikhe (approx 10% up)
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume increased by pressing Volume Up key."
            
        elif action == "down":
            # Volume down key ko 5 baar dabayenge (approx 10% down)
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume decreased by pressing Volume Down key."
            
        elif action == "full":
            # Safe side ke liye volume down 50 baar karke 0 karenge, phir up 50 baar karke 100% full
            for _ in range(50):
                pyautogui.press("volumeup")
            return "Volume set to maximum by simulating key presses."
            
        else:
            return f"Unknown action: {action}"
            
    except Exception as e:
        logger.error(f"Keyboard volume control error: {e}")
        return f"Failed to simulate volume keys: {e}"