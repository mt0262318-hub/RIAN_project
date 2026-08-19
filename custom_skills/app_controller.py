import logging
import subprocess
import os
from langchain_core.tools import tool

logger = logging.getLogger("rian.skills")

# Windows applications ka dynamic mapping registry
APP_REGISTRY = {
    "chrome": {"exe": "chrome.exe", "cmd": "chrome"},
    "vscode": {"exe": "Code.exe", "cmd": "code"},
    "notepad": {"exe": "notepad.exe", "cmd": "notepad"},
    "calculator": {"exe": "calc.exe", "cmd": "calc"},
    "spotify": {"exe": "Spotify.exe", "cmd": "spotify"}
}

@tool
def app_controller(action: str, app_name: str) -> str:
    """Opens or closes common desktop applications on the PC.
    Actions can be: 'open' or 'close'.
    Common app_names: 'chrome', 'vscode', 'notepad', 'calculator', 'spotify'.
    """
    action_clean = action.lower().strip()
    app_clean = app_name.lower().strip()

    # Agar app registry mein nahi hai toh fallback system chalayenge
    if app_clean not in APP_REGISTRY:
        if action_clean == "open":
            try:
                # Direct system shell execution try karenge
                subprocess.Popen(app_name, shell=True)
                return f"System registry entry not found, but attempted to open '{app_name}' via system shell."
            except Exception as e:
                return f"Application '{app_name}' is not recognized by the OS."
        return f"Cannot close '{app_name}' because its background process name is unknown."

    app_info = APP_REGISTRY[app_clean]

    try:
        if action_clean == "open":
            # subprocess.Popen use karne se background process fast chalti hai bina R.I.A.N. ko hang kiye
            subprocess.Popen(app_info["cmd"], shell=True)
            return f"Successfully sent launch signal to {app_name}."
            
        elif action_clean == "close":
            # Windows taskkill command se application process ko forcibly terminate karna
            kill_command = f"taskkill /f /im {app_info['exe']}"
            exit_code = os.system(kill_command)
            
            if exit_code == 0:
                return f"Successfully terminated {app_name} process."
            else:
                return f"Could not close {app_name}. It might not be running currently."
        else:
            return f"Invalid action: '{action}'. Only 'open' or 'close' are supported."
            
    except Exception as e:
        logger.error(f"App Controller critical error for {app_name}: {e}")
        return f"App automation failed: {str(e)}"