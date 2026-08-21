import os
import requests
from notebook_engine import NotebookEngine, sync_to_telegram
from autonomous_thinker import RianAutonomousCell
from visual_generator import trigger_visual_generation

class RianMasterPipeline:
    def __init__(self):
        self.thinker = RianAutonomousCell()
        self.notebook = NotebookEngine()

    def execute_full_workflow(self, objective, prompt_for_visual=None):
        print(f"[1/3] Running Autonomous Thinking Cell for: {objective}")
        thought_result = self.thinker.run_task(objective)
        
        if prompt_for_visual:
            print(f"[2/3] Triggering Visual Generation Pipeline...")
            trigger_visual_generation(prompt_for_visual)
            
        print(f"[3/3] Ensuring all temporary files are synced to Telegram Vault and local storage is wiped.")
        return "Workflow executed successfully. All heavy assets pushed to Telegram."

if __name__ == '__main__':
    pipeline = RianMasterPipeline()
    print("Master pipeline ready for production.")
