# memories/router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from .service import MemoryService
from .dto.dto import MemoryCreateRequest, MemorySearchRequest, CreateMemoryResponse

memories_router = APIRouter(prefix="/memories", tags=["Memories"])


def get_memory_service(db: Session = Depends(get_db)) -> MemoryService:
    return MemoryService(db)


@memories_router.post("/", response_model=CreateMemoryResponse)
def create_memory(
    request: MemoryCreateRequest,
    service: MemoryService = Depends(get_memory_service),
):
    return service.add_memory(
        user_id=request.user_id,
        content=request.content,
        importance=request.importance,
    )


@memories_router.get("/{user_id}")
def list_memories(user_id: str, service: MemoryService = Depends(get_memory_service)):
    return service.list_memories(user_id)


@memories_router.post("/{user_id}/search")
def search_memories(
    user_id: str,
    request: MemorySearchRequest,
    service: MemoryService = Depends(get_memory_service),
):
    return service.search_memories(
        user_id=user_id,
        search_text=request.search_text,
        similarity_threshold=request.similarity_threshold,
        top_k=request.top_k,
    )


@memories_router.get("/{user_id}/count")
def count_memories(user_id: str, service: MemoryService = Depends(get_memory_service)):
    return {"count": service.count_memories(user_id)}
