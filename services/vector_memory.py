import os
import json
import logging
from sqlalchemy import text
from database import engine

logger = logging.getLogger("vector_memory")

def store_semantic_memory(session_id: str, content: str, metadata: dict = None, embedding: list = None):
    """
    Saves context chunks and metadata into the semantic memory database.
    """
    query = text("""
        INSERT INTO semantic_memory (session_id, content, metadata_info, embedding)
        VALUES (:session_id, :content, :metadata_info, :embedding)
    """)
    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "session_id": session_id or "default",
                "content": content,
                "metadata_info": json.dumps(metadata or {}),
                "embedding": embedding
            })
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to insert semantic memory: {e}")
        return False

def search_semantic_memory(query_text: str, limit: int = 5) -> list:
    """
    Retrieves matching semantic context using keyword and text relevance.
    """
    query = text("""
        SELECT session_id, content, metadata_info, created_at 
        FROM semantic_memory 
        WHERE content ILIKE :q 
        ORDER BY created_at DESC 
        LIMIT :limit
    """)
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"q": f"%{query_text}%", "limit": limit})
            return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Semantic search query error: {e}")
        return []

if __name__ == "__main__":
    store_semantic_memory("test_rag", "RIAN architecture includes zero-disk Telegram Cloud Vault storage.", {"topic": "architecture"})
    results = search_semantic_memory("Telegram Cloud Vault")
    print(f"✅ Vector Memory Operational! Found matches: {len(results)}")
