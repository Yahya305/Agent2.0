# memories/service.py
from sqlalchemy.orm import Session
from core.database import get_db_context

class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_memory(self, user_id: str, content: str) -> dict:
        """
        Insert a new memory row.
        """
        query = """
            INSERT INTO semantic_memories (user_id, content)
            VALUES (:user_id, :content)
            RETURNING id, user_id, content, created_at;
        """
        result = self.db.execute(
            query,
            {"user_id": user_id, "content": content}
        )
        row = result.fetchone()
        return dict(row._mapping)

    def list_memories(self, user_id: str) -> list[dict]:
        """
        Fetch all memories for a given user.
        """
        query = """
            SELECT id, user_id, content, created_at
            FROM semantic_memories
            WHERE user_id = :user_id
            ORDER BY created_at DESC;
        """
        result = self.db.execute(query, {"user_id": user_id})
        return [dict(row._mapping) for row in result]
