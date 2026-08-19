import time
import asyncio
from typing import Dict, Any

class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.context: Dict[str, Any] = {}

    def touch(self):
        self.last_accessed = time.time()

class SessionManager:
    def __init__(self, ttl_seconds: int = 3600):
        self.sessions: Dict[str, UserSession] = {}
        self.ttl_seconds = ttl_seconds
        self._lock = asyncio.Lock()

    async def get_or_create_session(self, user_id: str) -> UserSession:
        async with self._lock:
            now = time.time()
            expired = [uid for uid, sess in self.sessions.items() if now - sess.last_accessed > self.ttl_seconds]
            for uid in expired:
                del self.sessions[uid]

            if user_id not in self.sessions:
                self.sessions[user_id] = UserSession(user_id)
            
            session = self.sessions[user_id]
            session.touch()
            return session

session_manager = SessionManager()
