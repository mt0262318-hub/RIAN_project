import os
import json
import time
import threading
import logging
import psutil
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger("rian.monitor")

PATTERN_FILE = '/home/ubuntu/RIAN_project/rian_patterns.json'

class ProactiveMonitor:
    def __init__(self, llm: ChatGroq, api_key: str):
        self.llm = llm
        self.api_key = api_key
        self.is_running = False
        
        # Dono tasks ke liye alag threads
        self.hardware_thread = None
        self.dream_thread = None
        self.dream_interval = 600  # 10 minute ka sleep cycle api bachane ke liye

    def start(self):
        if not self.is_running:
            self.is_running = True
            
            # Hardware Check Thread Start
            self.hardware_thread = threading.Thread(target=self._hardware_monitor_loop, daemon=True)
            self.hardware_thread.start()
            
            # Synthetic Learning Thread Start
            self.dream_thread = threading.Thread(target=self._dream_and_learn_loop, daemon=True)
            self.dream_thread.start()
            
            logger.info("Boss Level Unlocked: Hardware Monitor & Synthetic Learner started.")

    def stop(self):
        self.is_running = False
        if self.hardware_thread:
            self.hardware_thread.join(timeout=2)
        if self.dream_thread:
            self.dream_thread.join(timeout=2)
        logger.info("Proactive Monitor stopped safely.")

    # ==========================================
    # SYSTEM HARDWARE MONITOR (RAM & BATTERY)
    # ==========================================
    def _hardware_monitor_loop(self):
        """Monitors RAM and Battery every 60 seconds."""
        time.sleep(10)  # Initial boot delay
        while self.is_running:
            try:
                ram_usage = psutil.virtual_memory().percent
                battery = psutil.sensors_battery()
                
                trigger_alert = False
                alert_reason = ""
                
                if ram_usage > 90.0:
                    trigger_alert = True
                    alert_reason = f"RAM usage is critically high at {ram_usage}%."
                elif battery and battery.percent < 20 and not battery.power_plugged:
                    trigger_alert = True
                    alert_reason = f"Battery is low at {battery.percent}% and not charging."
                
                if trigger_alert:
                    logger.warning(f"Proactive Trigger Activated: {alert_reason}")
                    self._generate_proactive_alert(alert_reason)
                    
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error in hardware monitor thread: {e}")
                time.sleep(30)

    def _generate_proactive_alert(self, reason: str):
        """Generates a quick AI warning for hardware issues."""
        try:
            sys_prompt = "You are R.I.A.N., an autonomous system. Warn the user about the system issue in a single short, direct Hinglish sentence."
            messages = [
                SystemMessage(content=sys_prompt),
                HumanMessage(content=f"System Alert Reason: {reason}. Issue a short warning.")
            ]
            response = self.llm.invoke(messages)
            print(f"\n\n🚨 [R.I.A.N. PROACTIVE ALERT] >> {response.content.strip()}\n")
            print("[1] Voice Command 🎤 | [2] Type Command ⌨️ | [3] Exit ❌\nSelect Mode (1/2/3): ", end="", flush=True)
        except Exception as e:
            logger.error(f"Failed to generate hardware alert: {e}")

    # ==========================================
    # SYNTHETIC DATA GENERATOR (SELF-LEARNING)
    # ==========================================
    def _dream_and_learn_loop(self):
        """AI dreams up complex coding problems and learns from them when idle."""
        while self.is_running:
            time.sleep(self.dream_interval)
            
            if not self.is_running:
                break
                
            logger.info("System is idle. Initiating Synthetic Data Generation...")
            try:
                # STEP 1: Generate Problem
                generator_prompt = "You are the Synthetic Data Generator for R.I.A.N. Create a complex, realistic coding or logic problem. ONLY output the problem statement."
                problem_msg = self.llm.invoke([SystemMessage(content=generator_prompt)])
                synthetic_problem = problem_msg.content.strip()
                logger.info(f"Generated Problem: {synthetic_problem}")
                
                # STEP 2: Try to Solve
                solver_prompt = "You are R.I.A.N. Solve the following problem accurately and concisely."
                solution_msg = self.llm.invoke([SystemMessage(content=solver_prompt), HumanMessage(content=synthetic_problem)])
                synthetic_solution = solution_msg.content.strip()
                
                # STEP 3: Evaluate
                evaluator_prompt = "You are the Elite Evaluator. Review the problem and solution. If perfect, output 'PASS'. If flawed, extract a ONE-LINE strict rule starting with 'RULE:'."
                eval_msg = self.llm.invoke([SystemMessage(content=evaluator_prompt), HumanMessage(content=f"Problem: {synthetic_problem}\nSolution: {synthetic_solution}")])
                evaluation = eval_msg.content.strip()
                
                # STEP 4: Learn
                if "RULE:" in evaluation:
                    logger.warning(f"Self-Correction during idle time: {evaluation}")
                    self._save_synthetic_pattern(evaluation)
                else:
                    logger.info("Self-Test PASSED. No new rules needed.")
            except Exception as e:
                logger.error(f"Proactive Learning Error: {e}")

    def _save_synthetic_pattern(self, new_rule: str):
        """Saves learned rules permanently so the core AI remembers them."""
        try:
            patterns = []
            if os.path.exists(PATTERN_FILE):
                with open(PATTERN_FILE, 'r') as f:
                    patterns = json.load(f)
            
            clean_rule = new_rule.replace("RULE:", "").strip()
            if clean_rule not in patterns:
                patterns.append(clean_rule)
                with open(PATTERN_FILE, 'w') as f:
                    json.dump(patterns, f, indent=4)
                logger.info(f"Background Knowledge Expanded: {clean_rule}")
        except Exception as e:
            pass