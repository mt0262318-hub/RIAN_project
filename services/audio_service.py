import speech_recognition as sr
import asyncio
import logging

logger = logging.getLogger("rian.audio")

class AudioService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def speak_sync(self, text: str):
        """Blocking TTS function - Initialized locally to avoid Thread errors"""
        try:
            import pyttsx3
            # Engine ko har baar thread ke andar initialize karna zaroori hai
            engine = pyttsx3.init()
            engine.setProperty('rate', 170) 
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS Engine failed: {e}")

    async def speak(self, text: str):
        """Non-blocking async speak function"""
        # Ise alag thread mein chalayenge taaki system hang na ho
        await asyncio.to_thread(self.speak_sync, text)

    def listen_sync(self) -> str:
        """Blocking microphone listen function (internal use)"""
        with sr.Microphone() as source:
            print("\n🎤 Listening... (Boliye)")
            # Background noise ko samajhne ke liye 0.5 sec lega
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # 5 second tak wait karega, 10 second tak sunega
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                print("❌ Samajh nahi aaya, phir se koshish karein.")
                return ""
            except Exception as e:
                logger.error(f"Microphone error: {e}")
                return ""

    async def listen(self) -> str:
        """Non-blocking async listen function"""
        return await asyncio.to_thread(self.listen_sync)