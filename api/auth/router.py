# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from core.database import get_db
from .service import AuthService
from .dto.dto import RegisterRequest, LoginRequest

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@auth_router.post("/register", response_model=dict)
def register(
    data: RegisterRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    user = service.register_user(
        username=data.username,
        email=data.email,
        password=data.password,
        response=response
    )
    return {"id": user.id, "username": user.username, "email": user.email}


@auth_router.post("/login", response_model=dict)
def login(
    data: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    user = service.authenticate_user(
        email=data.email,
        password=data.password,
        response=response
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return {"message": "Login successful", "id": user.id, "username": user.username}