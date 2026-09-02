import os
import asyncio
from langchain_groq import ChatGroq
from langchain_core.tools import tool

@tool
def websearch(query: str) -> str:
    """Search the web for news."""
    return "Dummy news data"

async def test_agent():
    print("⏳ [1] Initializing RIAN Test Engine...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ [ERROR] GROQ_API_KEY missing in terminal!")
            return
            
        llm = ChatGroq(model_name="llama3-70b-8192", api_key=api_key, temperature=0.5)
        llm_with_tools = llm.bind_tools([websearch])
        
        print("🚀 [2] Sending Tool Command (Bypassing UI)...")
        res = await llm_with_tools.ainvoke("Internet se aaj ki news batao")
        
        print("\n✅ [SUCCESS] Backend is Perfect!")
        print("Tool Calls Generated:", res.tool_calls)
        print("\n🔥 CONCLUSION: Error is hidden inside your 'generate_rian_response' function!")
        
    except Exception as e:
        print("\n❌ [FAILED] API Error Details:")
        print(str(e))
        print("\n🔥 CONCLUSION: Your LangChain/Groq version is incompatible with tool choice!")

asyncio.run(test_agent())
