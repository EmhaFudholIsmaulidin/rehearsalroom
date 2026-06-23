from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.song import SongStatus


# ── Song Schemas ──────────────────────────────────────────────────────────────

class SongCreateRequest(BaseModel):
    title: str
    composer: Optional[str] = None
    duration_seconds: Optional[int] = None
    status: SongStatus = SongStatus.learning


class SongUpdateRequest(BaseModel):
    title: Optional[str] = None
    composer: Optional[str] = None
    duration_seconds: Optional[int] = None


class SongStatusUpdateRequest(BaseModel):
    status: SongStatus


class SongResponse(BaseModel):
    id: UUID
    band_id: UUID
    title: str
    composer: Optional[str]
    duration_seconds: Optional[int]
    status: SongStatus
    added_by: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class SongListResponse(BaseModel):
    items: list[SongResponse]
    total_count: int


# ── SongProgress Schemas ──────────────────────────────────────────────────────

class SongProgressCreateRequest(BaseModel):
    song_id: UUID
    progress_pct: int
    notes: Optional[str] = None

    @field_validator("progress_pct")
    @classmethod
    def validate_progress(cls, v: int) -> int:
        if v < 0 or v > 100:
            raise ValueError("Progress harus antara 0 dan 100")
        return v


class SongProgressResponse(BaseModel):
    id: UUID
    session_id: UUID
    song_id: UUID
    updated_by: Optional[UUID]
    progress_pct: int
    notes: Optional[str]
    updated_at: datetime
    song_title: Optional[str] = None

    model_config = {"from_attributes": True}


class SongProgressListResponse(BaseModel):
    items: list[SongProgressResponse]
    total_count: int
