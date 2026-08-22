import asyncio
import os
from langchain_openai import ChatOpenAI
from browser_use import Agent

async def run_autonomous_browser_task(task_prompt: str):
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "dummy"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini")
    )
    agent = Agent(
        task=task_prompt,
        llm=llm
    )
    result = await agent.run()
    return result

if __name__ == "__main__":
    print("Action Agent Engine Initialized & Ready!")
