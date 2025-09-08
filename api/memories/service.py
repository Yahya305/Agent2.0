# memories/service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from core.database import get_db
from models import SemanticMemory
from sentence_transformers import SentenceTransformer
from sqlalchemy import func, text
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
        )

    def get_embedding(self, text: str, is_query: bool = False) -> List[float]:
        try:
            prefix = "search_query: " if is_query else "search_document: "
            text = f"{prefix}{text}"
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return [0.0] * 768  # fallback vector

    def add_memory(self, user_id: str, content: str, importance: str = "medium"):
        embedding = self.get_embedding(content, is_query=False)

        new_memory = SemanticMemory(
            user_id=user_id,
            content=content,
            importance=importance,
            embedding=embedding,
        )
        self.db.add(new_memory)
        self.db.commit()
        self.db.refresh(new_memory)
        return new_memory

    def list_memories(self, user_id: str) -> list[SemanticMemory]:
        return (
            self.db.query(SemanticMemory)
            .filter(SemanticMemory.user_id == user_id)
            .order_by(SemanticMemory.created_at.desc())
            .all()
        )

    def search_memories(
        self,
        user_id: str,
        search_text: str,
        similarity_threshold: float = 0.2,
        top_k: int = 5,
    ):
        # Generate query embedding
        query_embedding = self.get_embedding(search_text, is_query=True)

        sql = text("""
            SELECT 
                id,
                content,
                importance,
                created_at,
                1 - (embedding <=> (:embedding)::vector) AS similarity
            FROM semantic_memories
            WHERE user_id = :user_id
            AND 1 - (embedding <=> (:embedding)::vector) > :threshold
            ORDER BY similarity DESC
            LIMIT :top_k
        """)

        rows = self.db.execute(
            sql,
            {
                "embedding": f"[{','.join(map(str, query_embedding))}]",  # send as pgvector literal
                "user_id": user_id,
                "threshold": similarity_threshold,
                "top_k": top_k,
            }
        ).fetchall()

        # Convert rows to dicts so FastAPI can serialize them
        results = [
            {
                "id": row.id,
                "content": row.content,
                "importance": row.importance,
                "created_at": row.created_at,
                "similarity": row.similarity,
            }
            for row in rows
        ]

        return results

    # --- NEW: Count user memories ---
    def count_memories(self, user_id: str) -> int:
        """
        Count how many memories a user has.
        """
        count = self.db.query(func.count(SemanticMemory.id)).filter(
            SemanticMemory.user_id == user_id
        ).scalar()
        return count
