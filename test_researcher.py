import os
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Environment Load
load_dotenv('/home/ubuntu/RIAN_project/.env')
key = os.getenv('GROQ_API_KEY')
# वर्किंग मॉडल सेट किया गया है 
model_name = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')

# Init LLM
llm = ChatGroq(model_name=model_name, api_key=key)
search_tool = DuckDuckGoSearchRun()

# Modern LangGraph Tool format using @tool decorator
@tool
def web_search(query: str) -> str:
    """Useful for finding current news and facts from the internet. Input should be a search query."""
    return search_tool.invoke(query)

tools = [web_search]

# Create Modern LangGraph Agent
agent_executor = create_react_agent(llm, tools)

print("\n[+] Researcher Agent (LangGraph) Online. Testing Live Search...\n")
try:
    inputs = {"messages": [("user", "What is the latest major breakthrough or news in Artificial Intelligence today? Explain clearly in Hindi.")]}
    response = agent_executor.invoke(inputs)
    
    print("\n[✓] FINAL AGENT RESPONSE:\n")
    print(response["messages"][-1].content)
except Exception as e:
    print("\n[!] Agent Error:", e)
