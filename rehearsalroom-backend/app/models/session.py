import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class SessionStatus(str, enum.Enum):
    upcoming = "upcoming"
    ongoing = "ongoing"
    completed = "completed"
    cancelled = "cancelled"


class RehearsalSession(Base):
    __tablename__ = "rehearsal_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    location = Column(String, nullable=True)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.upcoming)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    band = relationship("Band", back_populates="sessions")
    creator = relationship("User", back_populates="sessions_created")
    session_songs = relationship("SessionSong", back_populates="session", cascade="all, delete-orphan", order_by="SessionSong.order_index")
    progress_entries = relationship("SongProgress", back_populates="session", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="session", cascade="all, delete-orphan")


class SessionSong(Base):
    __tablename__ = "session_songs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("rehearsal_sessions.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(GUID(), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

    # Relationships
    session = relationship("RehearsalSession", back_populates="session_songs")
    song = relationship("Song", back_populates="session_songs")
