import logging
import base64
import os
from io import BytesIO
from PIL import ImageGrab
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

logger = logging.getLogger("rian.skills")

@tool
def analyze_screen(prompt: str = "Describe what is on the screen in detail.") -> str:
    """Takes a screenshot of the current PC screen and uses a Vision AI model to analyze it.
    Use this when the user asks 'what is on my screen', 'read my screen', or 'find the error on my screen'.
    You can pass a specific prompt to look for specific things."""
    try:
        # 1. Screen ka Screenshot lena
        logger.info("Capturing screenshot...")
        screenshot = ImageGrab.grab()
        # AI ko clearly dikhane ke liye image resolution optimize karna
        screenshot.thumbnail((1024, 1024))

        # 2. Image ko compress karke Base64 mein convert karna (taaki API fast chale)
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG", quality=70) 
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
       # 3. API Key check karna (Force loading from .env)
        from dotenv import load_dotenv
        load_dotenv()  # Yeh forcefully tumhari .env file se keys uthayega
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: GROQ_API_KEY not found in environment variables."
        
      # 4. Groq ka latest Llama-4 Vision Model call karna (2026 Updated)
        logger.info("Sending image to Llama-4-Scout Vision model...")
        vision_chat = ChatGroq(
            model_name="meta-llama/llama-4-scout-17b-16e-instruct", # <-- Naya Model ID
            api_key=api_key,
            max_tokens=1024
        )
        
        # Langchain format mein Image bhejna
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_str}"},
                },
            ]
        )
        
        # 5. Vision model ka answer nikal kar main R.I.A.N. ko wapas dena
        response = vision_chat.invoke([message])
        return f"Vision Analysis Result: {response.content}"
        
    except Exception as e:
        logger.error(f"Screen analysis failed: {e}")
        return f"Failed to analyze screen: {str(e)}"