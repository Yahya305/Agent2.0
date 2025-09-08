# memories/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from .service import MemoryService

router = APIRouter(prefix="/memories", tags=["Memories"])

# Dependency to provide the service
def get_memory_service(db: Session = Depends(get_db)) -> MemoryService:
    return MemoryService(db)

@router.post("/")
def create_memory(
    user_id: str,
    content: str,
    service: MemoryService = Depends(get_memory_service),
):
    return service.add_memory(user_id=user_id, content=content)

@router.get("/{user_id}")
def list_memories(
    user_id: str,
    service: MemoryService = Depends(get_memory_service),
):
    return service.list_memories(user_id)
