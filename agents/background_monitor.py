import time
import threading
import logging
import psutil
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger("rian.monitor")

class ProactiveMonitor(threading.Thread):
    def __init__(self, llm: ChatGroq, api_key: str):
        super().__init__()
        self.llm = llm
        self.api_key = api_key
        self.running = True
        self.daemon = True  # Main program band hote hi yeh thread bhi safely band ho jayega
        
    def run(self):
        logger.info("Proactive Background Monitor Thread Started.")
        # Ek initial delay taaki main system pehle completely boot ho jaye
        time.sleep(10) 
        
        while self.running:
            try:
                # Hardware Stats Check Karna
                ram_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent(interval=1)
                battery = psutil.sensors_battery()
                
                trigger_alert = False
                alert_reason = ""
                
                # Critical Threshold Limits Set Karna
                if ram_usage > 90.0:
                    trigger_alert = True
                    alert_reason = f"RAM usage is critically high at {ram_usage}%."
                elif battery and battery.percent < 20 and not battery.power_plugged:
                    trigger_alert = True
                    alert_reason = f"Battery is low at {battery.percent}% and not charging."
                
                # Agar koi limit cross hui, toh AI khud active hoga
                if trigger_alert:
                    logger.warning(f"Proactive Trigger Activated: {alert_reason}")
                    self.generate_proactive_alert(alert_reason)
                    
                # Har 60 seconds (1 minute) mein check karega
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in background monitor thread: {e}")
                time.sleep(30) # Error aane par pause lenge
                
    def generate_proactive_alert(self, reason: str):
        """Background se direct Groq LLM ko call karke user ke liye warning message nikalna"""
        try:
            sys_prompt = "You are R.I.A.N., a desktop assistant. You have detected a system issue. Warn the user about it in a single short, direct, and helpful Hindi/Hinglish sentence. Do not say anything extra."
            messages = [
                SystemMessage(content=sys_prompt),
                HumanMessage(content=f"System Alert Reason: {reason}. Issue a short direct warning statement.")
            ]
            response = self.llm.invoke(messages)
            
            # Terminal loop ko interrupt kiye bina directly screen par push karna
            print(f"\n\n🚨 [R.I.A.N. PROACTIVE ALERT] >> {response.content}\n")
            print("[1] Voice Command 🎤 | [2] Type Command ⌨️ | [3] Exit ❌\nSelect Mode (1/2/3): ", end="", flush=True)
            
        except Exception as e:
            logger.error(f"Failed to generate proactive AI response: {e}")

    def stop(self):
        self.running = False