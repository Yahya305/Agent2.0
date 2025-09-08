from pydantic import BaseModel
from typing import Optional


class MemoryCreateRequest(BaseModel):
    user_id: str
    content: str
    importance: Optional[str] = "medium"


class MemorySearchRequest(BaseModel):
    search_text: str
    similarity_threshold: float = 0.75
    top_k: int = 5
