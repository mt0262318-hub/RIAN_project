import logging
from config.settings import settings

logger = logging.getLogger("rian.vector_db")

class VectorDBManager:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self.init_client()

    def init_client(self):
        try:
            from qdrant_client import QdrantClient
            if hasattr(settings, 'qdrant_url') and settings.qdrant_url:
                self.client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=getattr(settings, 'qdrant_api_key', None),
                    timeout=3.0
                )
                self.client.get_collections()
                self.is_connected = True
                logger.info("Qdrant Vector DB connected successfully.")
            else:
                logger.warning("No Qdrant URL provided, running in local fallback.")
        except Exception as e:
            self.is_connected = False
            self.client = None
            logger.warning(f"Qdrant connection bypassed (Safe Mode): {e}")

    def add_documents(self, documents):
        return True if self.is_connected else False

    def search(self, query, top_k=3):
        return []

vector_db = VectorDBManager()
