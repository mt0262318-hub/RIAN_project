import json
import os
from datetime import datetime

MEMORY_FILE = "rian_longterm_memory.json"

class MemoryLearner:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump({"facts": [], "preferences": {}, "interaction_history": []}, f, indent=2)

    def learn_fact(self, key_insight: str):
        with open(self.memory_file, "r") as f:
            data = json.load(f)
        
        timestamp = datetime.now().isoformat()
        data["facts"].append({"timestamp": timestamp, "fact": key_insight})
        
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[Memory Engine] Learned & Stored: {key_insight}")

    def recall_context(self) -> str:
        with open(self.memory_file, "r") as f:
            data = json.load(f)
        facts = [item["fact"] for item in data.get("facts", [])][-10:]
        return "\n".join(facts)

if __name__ == "__main__":
    learner = MemoryLearner()
    learner.learn_fact("System initialization completed with continuous learning engine.")
    print("[✓] Memory Learner Engine Active.")