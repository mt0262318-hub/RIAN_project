import datetime
import logging
from typing import Any, Dict, List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import settings

logger = logging.getLogger("rian.memory")

class MemoryManager:
    def __init__(self) -> None:
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embeddings_model)
        self.db = Chroma(
            persist_directory=settings.chroma_dir,
            embedding_function=self.embeddings,
        )
        logger.info("MemoryManager initialized.")

    def remember(self, text: str, metadata: Dict[str, Any] | None = None) -> str:
        payload = metadata or {}
        payload["timestamp"] = datetime.datetime.now().isoformat()
        doc_ids = self.db.add_texts([text], metadatas=[payload])
        return doc_ids[0] if doc_ids else "success"

    def recall(self, query: str, k: int = 3) -> List[str]:
        # 1. Similarity search from vector db
        results = self.db.similarity_search(query, k=k)
        recalled_texts = [doc.page_content for doc in results]

        # 2. Safety Net: If asking about name/identity, explicitly fetch latest stored facts/messages
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in ["naam", "name", "who am i", "kya hai"]):
            try:
                all_data = self.db.get()
                if all_data and "documents" in all_data and all_data["documents"]:
                    # Grab last 10 documents to ensure user facts/name are never missed
                    recent_docs = all_data["documents"][-10:]
                    for doc in recent_docs:
                        if doc not in recalled_texts and ("manish" in doc.lower() or "naam" in doc.lower() or "name" in doc.lower()):
                            recalled_texts.insert(0, doc)
            except Exception as e:
                logger.error(f"Fallback memory recall failed: {e}")

        return recalled_texts

    def stats(self) -> Dict[str, Any]:
        data = self.db.get()
        count = len(data["ids"]) if data and "ids" in data else 0
        return {"memory_points": count}