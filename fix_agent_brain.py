import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Strict system instruction for clean direct execution without meta-thinking
clean_prompt_patch = '''
SYSTEM_INSTRUCTION = """You are R.I.A.N., an elite AI assistant.
Directives:
1. Speak in natural, crisp Hinglish/English.
2. NEVER output your internal thoughts, self-critique, drafts, or reasoning steps like 'Polish:', 'Matches perfectly', or '<think>'.
3. Always respond directly in 1 short sentence confirming the action taken."""
'''

if "SYSTEM_INSTRUCTION =" not in content:
    content = clean_prompt_patch + "\n" + content

# Ensure broadcast triggers on common intents cleanly
trigger_logic = """
        q_clean = query.lower().strip() if isinstance(query, str) else ""
        
        # OS Level Direct Trigger
        if "notepad" in q_clean:
            await manager.broadcast({"action": "open_app", "target": "notepad"})
        elif "youtube" in q_clean:
            await manager.broadcast({"action": "open_url", "target": "https://youtube.com"})
        elif "edge" in q_clean or "browser" in q_clean:
            await manager.broadcast({"action": "open_app", "target": "msedge"})
"""

if "await manager.broadcast({\"action\": \"open_app\"" not in content:
    content = content.replace("final_output = local_llm.generate", trigger_logic + "\n        final_output = local_llm.generate")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Agent brain & dispatch rules cleaned up.")
