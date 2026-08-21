import asyncio
import time
import os
from duckduckgo_search import DDGS
import chromadb

client = chromadb.PersistentClient(path="./rian_memory")
collection = client.get_or_create_collection(name="autonomous_knowledge")

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
            combined_text = "\n".join([f"- {r.get('title', '')}: {r.get('body', '')}" for r in results])
            doc_id = f"auto_{int(time.time())}_{topic.replace(' ', '_')}"
            collection.add(
                documents=[f"Autonomous Learning ({topic}):\n{combined_text}"],
                metadatas=[{"source": "autonomous_learner", "topic": topic, "timestamp": str(time.time())}],
                ids=[doc_id]
            )
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully learned & saved: {topic}", flush=True)
    except Exception as e:
        print(f"Error learning topic {topic}: {e}", flush=True)

async def continuous_learning_loop():
    print("R.I.A.N. 24/7 Autonomous Learning Engine Started...", flush=True)
    while True:
        for topic in TOPICS:
            synthesize_knowledge(topic)
            await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(continuous_learning_loop())
