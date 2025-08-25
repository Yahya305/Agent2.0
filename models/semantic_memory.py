from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from core.database import Base  # your shared Base from database.py


class SemanticMemory(Base):
    __tablename__ = "semantic_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    content = Column(String, nullable=False)
    importance = Column(String, default="medium")


    
    embedding = Column(Vector(768))  # pgvector column
    created_at = Column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
