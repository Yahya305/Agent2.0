from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base


class UserSession(Base):
    __tablename__ = "user_session"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    refresh_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)          # When the refresh token expires
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), onupdate=func.now())  # Update each time token is used

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    is_valid = Column(Boolean, default=True)              # For revocation / logout
