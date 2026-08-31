import os
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

def route_task(user_query: str) -> str:
    """Master Router logic for R.I.A.N."""
    system_prompt = """You are the Master Planestrator (Router) for an advanced Agentic AI system.
    Analyze the user's prompt and route it to the exact specialist department.
    CRITICAL RULE: Output ONLY ONE of the following words, with absolutely no other text, punctuation, or explanation:
    
    CODER (If the query involves math, algorithms, Python, or data analysis)
    RESEARCHER (If the query asks for real-time news, live facts, weather, or web search)
    PC_CONTROL (If the query asks to open an app, play YouTube, or control the physical laptop)
    GENERAL (If it is just normal chat, greetings, or basic questions)"""
    
    inputs = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]
    
    response = llm.invoke(inputs)
    return response.content.strip().upper()

print("\n[+] Planestrator Router Online. Testing Decision Engine...\n")
try:
    test_queries = [
        "Ek python script likho jo 1 se 100 tak prime numbers print kare",
        "Aaj ki taza khabar kya hai?",
        "Mera chrome browser khol do",
        "Tumhara naam kya hai aur tum kaise ho?"
    ]
    
    for query in test_queries:
        print(f"[USER] : {query}")
        print(f"[ROUTER] -> Sending to: {route_task(query)}\n")
        
except Exception as e:
    print("\n[!] Router Error:", str(e))
