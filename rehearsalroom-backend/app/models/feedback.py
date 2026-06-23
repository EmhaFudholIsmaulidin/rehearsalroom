import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("rehearsal_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("RehearsalSession", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")
