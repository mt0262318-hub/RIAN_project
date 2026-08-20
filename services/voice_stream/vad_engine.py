import logging
import numpy as np

logger = logging.getLogger("vad_engine")

class VoiceActivityEngine:
    """
    Ultra-lightweight energy & amplitude detector for real-time audio barge-in.
    """
    def __init__(self, energy_threshold: float = 0.015):
        self.energy_threshold = energy_threshold

    def is_speech(self, raw_audio_chunk: bytes) -> bool:
        if not raw_audio_chunk:
            return False
        try:
            audio_data = np.frombuffer(raw_audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
            rms_energy = np.sqrt(np.mean(audio_data**2))
            return bool(rms_energy > self.energy_threshold)
        except Exception as e:
            logger.error(f"VAD Frame error: {e}")
            return False
