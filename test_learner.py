import os
import json
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Environment Setup
load_dotenv('/home/ubuntu/RIAN_project/.env')
key = os.getenv('GROQ_API_KEY')
model_name = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')

llm = ChatGroq(model_name=model_name, api_key=key, temperature=0.1)
PATTERN_FILE = '/home/ubuntu/RIAN_project/rian_patterns.json'

def learn_from_error(task: str, error_msg: str):
    print(f"\n[!] ERROR DETECTED in Task: {task}")
    print(f"[!] Error Details: {error_msg}")
    print("\n[*] Initializing Meta-Cognition (Reflection) Module...")
    
    learner_prompt = """You are the Meta-Cognition (Self-Learning) Module of R.I.A.N.
    Your job is to analyze failed tasks and errors, and extract a strict ONE-LINE rule to prevent this exact error in the future.
    Do not explain or write paragraphs. Return ONLY the extracted rule starting with 'RULE:'."""
    
    user_input = f"Task Attempted: {task}\nError Received: {error_msg}\nWhat is the rule to avoid this?"
    
    inputs = [
        SystemMessage(content=learner_prompt),
        HumanMessage(content=user_input)
    ]
    
    try:
        response = llm.invoke(inputs)
        new_pattern = response.content.strip()
        
        print(f"\n[+] Pattern Extracted: {new_pattern}")
        
        # Memory me Save karna (JSON file)
        patterns = []
        if os.path.exists(PATTERN_FILE):
            with open(PATTERN_FILE, 'r') as f:
                patterns = json.load(f)
                
        patterns.append(new_pattern)
        
        with open(PATTERN_FILE, 'w') as f:
            json.dump(patterns, f, indent=4)
            
        print(f"[+] Pattern permanently saved to {PATTERN_FILE}. Total Patterns Learned: {len(patterns)}\n")
        
    except Exception as e:
        print(f"\n[!] Learner Error: {str(e)}")

# Ek fake error simulate kar rahe hain test karne ke liye
learn_from_error(
    task="Write a python script to fetch a webpage using requests.", 
    error_msg="NameError: name 'requests' is not defined. Did you forget to import requests?"
)
