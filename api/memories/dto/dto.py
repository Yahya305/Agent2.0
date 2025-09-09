from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class MemoryCreateRequest(BaseModel):
    user_id: str
    content: str
    importance: Optional[str] = "medium"

class SemanticMemoryDTO(BaseModel):
    id: UUID
    user_id: UUID  
    content: str
    importance: str
    created_at: datetime

    class Config:
        orm_mode = True


class MemorySearchRequest(BaseModel):
    search_text: str
    similarity_threshold: float = 0.75
    top_k: int = 5
