import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    bands_created = relationship("Band", back_populates="creator", foreign_keys="Band.created_by")
    band_memberships = relationship("BandMember", back_populates="user")
    songs_added = relationship("Song", back_populates="added_by_user", foreign_keys="Song.added_by")
    sessions_created = relationship("RehearsalSession", back_populates="creator")
    feedbacks = relationship("Feedback", back_populates="user")
    invitations_sent = relationship("Invitation", back_populates="inviter", foreign_keys="Invitation.invited_by")
    song_progresses = relationship("SongProgress", back_populates="updater")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
