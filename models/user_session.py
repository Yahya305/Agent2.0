from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserSession(Base):
    __tablename__ = "user_session"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    refresh_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # When the refresh token expires
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), onupdate=func.now())

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    is_valid = Column(Boolean, default=True)
