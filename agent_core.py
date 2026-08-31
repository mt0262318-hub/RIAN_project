import os
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

def process_with_agent(user_query, api_key, model_name="openai/gpt-oss-20b"):
    try:
        llm = ChatGroq(model_name=model_name, api_key=api_key)
        search_tool = DuckDuckGoSearchRun()

        @tool
        def web_search(query: str) -> str:
            """Useful for finding current news, facts, live updates, weather, and real-time information from the internet. Input should be a concise search query."""
            return search_tool.invoke(query)

        tools = [web_search]
        
        # STRICT System prompt for Hinglish output
        system_prompt = "You are System R.I.A.N., an advanced AI assistant. You have access to a web_search tool. Use it ONLY if the user asks for real-time news, current events, or facts you don't know. CRITICAL RULE: You must ALWAYS generate your final response in conversational Hinglish (Hindi words written in English/Roman alphabet). NEVER use Devanagari script. Keep the tone natural, helpful, and tech-savvy. Format with Markdown if needed."
        
        agent_executor = create_react_agent(llm, tools, state_modifier=system_prompt)
        
        inputs = {"messages": [("user", user_query)]}
        response = agent_executor.invoke(inputs)
        return response["messages"][-1].content
    except Exception as e:
        return f"Agent Logic Error: {str(e)}"
