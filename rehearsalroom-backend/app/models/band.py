import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class MemberRole(str, enum.Enum):
    band_leader = "band_leader"
    member = "member"


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"


class Band(Base):
    __tablename__ = "bands"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    genre = Column(String, nullable=True)
    formed_year = Column(Integer, nullable=True)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    creator = relationship("User", back_populates="bands_created", foreign_keys=[created_by])
    members = relationship("BandMember", back_populates="band", cascade="all, delete-orphan")
    songs = relationship("Song", back_populates="band", cascade="all, delete-orphan")
    sessions = relationship("RehearsalSession", back_populates="band", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="band", cascade="all, delete-orphan")


class BandMember(Base):
    __tablename__ = "band_members"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MemberRole), nullable=False, default=MemberRole.member)
    instrument = Column(String, nullable=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    band = relationship("Band", back_populates="members")
    user = relationship("User", back_populates="band_memberships")


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    invited_email = Column(String, nullable=False)
    invited_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(InvitationStatus), nullable=False, default=InvitationStatus.pending)
    token = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    band = relationship("Band", back_populates="invitations")
    inviter = relationship("User", back_populates="invitations_sent", foreign_keys=[invited_by])
