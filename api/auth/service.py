# app/auth/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from passlib.context import CryptContext
from models import User, UserSession
from datetime import datetime, timedelta, timezone
from core.constants import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def register_user(self, username: str, email: str, password: str, response: Response) -> User:
        """
        Register a new user, create tokens, set access_token in cookie,
        and store refresh_token in DB.
        """
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

        # --- Create tokens ---
        access_token = self.create_access_token(new_user)
        self.create_refresh_token(new_user)


        # Set access token in httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # set True in production HTTPS
            samesite="lax",
        )

        return new_user
    
    def authenticate_user(self, email: str, password: str, response: Response) -> User | None:
        """
        Authenticate user and issue tokens.
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None

        access_token = self.create_access_token(user)
        self.create_refresh_token(user)

        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # set True in production HTTPS
            samesite="lax",
        )

        return user
    
    def create_access_token(self, user: User) -> str:
        payload = {
            "userId": user.id,
            "username": user.username,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        token = jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm="HS256")
        return token
    
    def create_refresh_token(self, user: User) -> UserSession:
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"userId": user.id, "exp": expires_at}
        token = jwt.encode(payload, REFRESH_TOKEN_SECRET, algorithm="HS256")

        # Check if a session exists for this user + device
        session = (
            self.db.query(UserSession)
            .filter(
                UserSession.user_id == user.id,
                UserSession.ip_address == "127.0.0.1",  # mock
                UserSession.user_agent == "mock-agent"  # mock
            )
            .first()
        )

        if session:
            # Update existing session
            session.refresh_token = token
            session.expires_at = expires_at
            session.is_valid = True
            self.db.commit()
            self.db.refresh(session)
        else:
            # Create a new session
            session = UserSession(
                user_id=user.id,
                refresh_token=token,
                expires_at=expires_at,
                ip_address="127.0.0.1",
                user_agent="mock-agent",
                is_valid=True,
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

        return session
    
    def verify_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
            return {"userId": payload["userId"], "username": payload["username"], "email": payload["email"]}
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Access token expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    def verify_refresh_token(self, token: str) -> UserSession | None:
        try:
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

        session = self.db.query(UserSession).filter(
            UserSession.refresh_token == token,
            UserSession.is_valid == True,
            UserSession.expires_at > datetime.now(timezone.utc),
        ).first()

        if not session:
            return None

        # Lazy load user for convenience
        session.user = self.db.query(User).filter(User.id == session.user_id).first()
        return session
