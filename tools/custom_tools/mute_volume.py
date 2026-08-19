import logging
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from langchain_core.tools import tool

logger = logging.getLogger("rian.skills")

@tool
def mute_volume() -> str:
    """Mutes the master volume of the PC using the pycaw library."""
    try:
        # Get default audio device
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Mute status set to True (1)
        volume.SetMute(1, None)
        return "Master volume has been successfully muted."
    except Exception as e:
        logger.error(f"Failed to mute volume: {e}")
        return f"Error while muting volume: {e}"