# app/auth/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user using ORM.
        """
        # Check if user already exists
        existing = (
            self.db.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        new_user = User(
            username=username,
            email=email,
            hashed_password=self.hash_password(password),
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Authenticate user via ORM query.
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
