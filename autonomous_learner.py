import asyncio
import time
from duckduckgo_search import DDGS
from memory.chroma_store import memory_store

TOPICS = [
    "advanced system architecture patterns",
    "python fast asynchronous pipelines",
    "distributed ai agent communication",
    "modern vector database optimizations"
]

def synthesize_knowledge(topic: str):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=3))
            if not results:
                return
            combined_text = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            memory_store.add_texts(
                texts=[f"Autonomous Learning ({topic}):\n{combined_text}"],
                metadatas=[{"source": "autonomous_learner", "topic": topic, "timestamp": str(time.time())}]
            )
            print(f"Learned and vectorized topic: {topic}")
    except Exception as e:
        print(f"Error learning topic {topic}: {e}")

async def continuous_learning_loop():
    print("R.I.A.N. 24/7 Autonomous Learning Engine Started...")
    while True:
        for topic in TOPICS:
            synthesize_knowledge(topic)
            await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(continuous_learning_loop())
