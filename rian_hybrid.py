import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
import groq
from google import genai # Naya, updated import

# ==========================================
# API KEYS (Yahan apni original keys paste karna)
# ==========================================
GROQ_API_KEY = "yahan_apni_groq_key_paste_karo"
GEMINI_API_KEY = "yahan_apni_gemini_key_paste_karo"

# ==========================================
# BACKEND: Smart Cloud API Thread (No UI Freeze)
# ==========================================
class CloudAPIWorker(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        try:
            # LOGIC: Agar sawal mein "socho", "samjhao", "code" ya "explain" word hai, toh Gemini
            trigger_words = ["socho", "samjhao", "code", "explain"]
            use_gemini = any(word in self.user_input.lower() for word in trigger_words)

            if use_gemini:
                print("\n🧠 R.I.A.N. (Gemini Mode) deep thinking kar rahi hai...")
                # Naye Google GenAI SDK ka syntax
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=self.user_input
                )
                reply = response.text
            
            else:
                print("\n⚡ R.I.A.N. (Groq Mode) fast reply soch rahi hai...")
                client = groq.Groq(api_key=GROQ_API_KEY)
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": self.user_input}],
                    model="openai/gpt-oss-120b", 
                )
                reply = chat_completion.choices[0].message.content

            self.response_ready.emit(reply)

        except Exception as e:
            self.response_ready.emit(f"System Error: {str(e)}")

# ==========================================
# FRONTEND: Transparent Glowing Ring UI
# ==========================================
class RianInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 300)

        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_ring)
        self.timer.start(20) 

        self.is_thinking = False

    def animate_ring(self):
        if self.is_thinking:
            self.angle = (self.angle + 10) % 360 
        else:
            self.angle = (self.angle + 3) % 360  
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        glow_color = QColor(0, 255, 255, 200) if not self.is_thinking else QColor(255, 50, 50, 200)
        pen = QPen(glow_color, 8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        painter.drawArc(50, 50, 200, 200, self.angle * 16, 270 * 16)

    def mousePressEvent(self, event):
        if not self.is_thinking:
            self.is_thinking = True
            
            test_prompt = "Hello R.I.A.N, Python ka ek simple loop ka code batao."
            print(f"\nUser Query: {test_prompt}")
            
            self.worker = CloudAPIWorker(test_prompt)
            self.worker.response_ready.connect(self.on_cloud_response)
            self.worker.start()

    def on_cloud_response(self, reply):
        print(f"\n--- R.I.A.N. Jawab ---\n{reply}\n----------------------")
        self.is_thinking = False 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RianInterface()
    window.show()
    sys.exit(app.exec_())