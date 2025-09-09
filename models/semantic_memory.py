import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class SemanticMemory(Base):
    __tablename__ = "semantic_memories"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(String, nullable=False)
    importance = Column(String, default="medium")

    embedding = Column(Vector(768))  # pgvector column
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
