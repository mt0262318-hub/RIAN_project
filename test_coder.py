import os
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.tools import PythonREPLTool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage

# Environment Setup
load_dotenv('/home/ubuntu/RIAN_project/.env')
key = os.getenv('GROQ_API_KEY')
model_name = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')

llm = ChatGroq(model_name=model_name, api_key=key)

# The New Tool: Python execution environment
python_repl_tool = PythonREPLTool()
tools = [python_repl_tool]

# Create agent WITHOUT state_modifier to avoid version conflicts
agent_executor = create_react_agent(llm, tools)

print("\n[+] Coder Agent Online. Testing Code Execution...\n")
try:
    test_query = "Write a python script to calculate the 15th Fibonacci number, run it, and tell me the answer."
    print(f"User Query: {test_query}\n")
    
    system_prompt = "You are a highly skilled Python Coder Agent. You have access to a Python REPL tool. If the user asks a mathematical question, requires data analysis, or wants to run an algorithm, you MUST write the Python code and execute it using the tool. Always print the result in your code so the tool can capture the output. Return the final answer based on the execution result."
    
    # Pass SystemMessage directly in the input stream (Bulletproof method)
    inputs = {"messages": [
        SystemMessage(content=system_prompt),
        HumanMessage(content=test_query)
    ]}
    
    response = agent_executor.invoke(inputs)
    
    print("\n[✓] FINAL AGENT RESPONSE:\n")
    print(response["messages"][-1].content)
except Exception as e:
    print("\n[!] Agent Error:", str(e))
