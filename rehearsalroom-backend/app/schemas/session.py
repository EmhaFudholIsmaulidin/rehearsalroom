from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.session import SessionStatus
from app.schemas.song import SongResponse, SongProgressResponse


# ── RehearsalSession Schemas ──────────────────────────────────────────────────

class SessionCreateRequest(BaseModel):
    title: str
    scheduled_at: datetime
    duration_minutes: int
    location: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None


class SessionStatusUpdateRequest(BaseModel):
    status: SessionStatus


class SessionSongResponse(BaseModel):
    id: UUID
    session_id: UUID
    song_id: UUID
    order_index: int
    song: Optional[SongResponse] = None

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    id: UUID
    band_id: UUID
    title: str
    scheduled_at: datetime
    duration_minutes: int
    location: Optional[str]
    status: SessionStatus
    created_by: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionDetailResponse(SessionResponse):
    session_songs: List[SessionSongResponse] = []
    progress_entries: List[SongProgressResponse] = []

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    total_count: int


# ── SessionSong Schemas ───────────────────────────────────────────────────────

class AddSongToSessionRequest(BaseModel):
    song_id: UUID
    order_index: Optional[int] = None


class ReorderSessionSongsRequest(BaseModel):
    song_orders: List[dict]
    # Expected: [{"song_id": "uuid", "order_index": 0}, ...]
