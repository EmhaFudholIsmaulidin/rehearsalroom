import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class SongStatus(str, enum.Enum):
    learning = "learning"
    ready = "ready"
    on_hold = "on_hold"


class Song(Base):
    __tablename__ = "songs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    composer = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(Enum(SongStatus), nullable=False, default=SongStatus.learning)
    added_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    band = relationship("Band", back_populates="songs")
    added_by_user = relationship("User", back_populates="songs_added", foreign_keys=[added_by])
    session_songs = relationship("SessionSong", back_populates="song", cascade="all, delete-orphan")
    progress_entries = relationship("SongProgress", back_populates="song", cascade="all, delete-orphan")


class SongProgress(Base):
    __tablename__ = "song_progresses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("rehearsal_sessions.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(GUID(), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    updated_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    progress_pct = Column(Integer, nullable=False, default=0)
    notes = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("RehearsalSession", back_populates="progress_entries")
    song = relationship("Song", back_populates="progress_entries")
    updater = relationship("User", back_populates="song_progresses")
