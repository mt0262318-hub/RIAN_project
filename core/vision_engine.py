import requests
import base64
import os

class VisionEngine:
    def __init__(self, model_name: str = "llava:7b", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.generate_url = f"{base_url}/api/generate"

    def analyze_image(self, prompt: str, image_path: str) -> str:
        if not os.path.exists(image_path):
            return f"Error: Image file not found at {image_path}"

        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }
        try:
            response = requests.post(self.generate_url, json=payload, timeout=90)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return f"Vision Error: Code {response.status_code}"
        except Exception as e:
            return f"Vision Exception: {str(e)}"

vision_engine = VisionEngine()
