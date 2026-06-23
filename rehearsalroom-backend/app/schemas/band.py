from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.band import MemberRole, InvitationStatus


# ── Band Schemas ──────────────────────────────────────────────────────────────

class BandCreateRequest(BaseModel):
    name: str
    genre: Optional[str] = None
    formed_year: Optional[int] = None


class BandUpdateRequest(BaseModel):
    name: Optional[str] = None
    genre: Optional[str] = None
    formed_year: Optional[int] = None


class BandResponse(BaseModel):
    id: UUID
    name: str
    genre: Optional[str]
    formed_year: Optional[int]
    created_by: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class BandListResponse(BaseModel):
    items: list[BandResponse]
    total_count: int


# ── BandMember Schemas ────────────────────────────────────────────────────────

class BandMemberResponse(BaseModel):
    id: UUID
    band_id: UUID
    user_id: UUID
    role: MemberRole
    instrument: Optional[str]
    joined_at: datetime
    username: Optional[str] = None
    email: Optional[str] = None

    model_config = {"from_attributes": True}


class BandMemberUpdateRequest(BaseModel):
    role: Optional[MemberRole] = None
    instrument: Optional[str] = None


class BandMemberListResponse(BaseModel):
    items: list[BandMemberResponse]
    total_count: int


# ── Invitation Schemas ────────────────────────────────────────────────────────

class InvitationCreateRequest(BaseModel):
    invited_email: EmailStr


class InvitationResponse(BaseModel):
    id: UUID
    band_id: UUID
    invited_email: str
    invited_by: Optional[UUID]
    status: InvitationStatus
    token: str
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class InvitationListResponse(BaseModel):
    items: list[InvitationResponse]
    total_count: int


class AcceptInvitationRequest(BaseModel):
    token: str
