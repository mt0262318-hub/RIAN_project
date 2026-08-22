import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent

async def run_autonomous_browser_agent(task_prompt: str):
    """Executes end-to-end autonomous visual navigation tasks."""
    try:
        # Initializing high-speed vision controller
        llm = ChatOpenAI(model="gpt-4o")
        agent = Agent(
            task=task_prompt,
            llm=llm
        )
        history = await agent.run()
        return {"status": "success", "result": str(history)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    test_task = "Go to YouTube, search for Arijit Singh latest songs, and click on the first video to play."
    asyncio.run(run_autonomous_browser_agent(test_task))
