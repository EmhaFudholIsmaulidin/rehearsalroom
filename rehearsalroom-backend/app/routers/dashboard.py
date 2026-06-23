from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_band_membership
from app.models.song import Song, SongStatus, SongProgress
from app.models.session import RehearsalSession, SessionStatus
from app.models.feedback import Feedback
from app.models.band import BandMember

router = APIRouter(tags=["Dashboard"])


class SessionSummary(BaseModel):
    id: UUID
    title: str
    scheduled_at: datetime
    status: str
    location: Optional[str] = None


class SongProgressSummary(BaseModel):
    song_id: UUID
    song_title: str
    latest_progress_pct: Optional[int] = None


class FeedbackSummary(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    username: Optional[str] = None


class DashboardResponse(BaseModel):
    total_songs: int
    ready_songs: int
    ready_pct: float
    total_members: int
    upcoming_sessions: List[SessionSummary]
    latest_feedbacks: List[FeedbackSummary]
    song_progress_summary: List[SongProgressSummary]


@router.get(
    "/bands/{band_id}/dashboard",
    response_model=DashboardResponse,
    summary="Agregat data dashboard band",
)
def get_dashboard(
    band_id: UUID,
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    # ── Song stats ────────────────────────────────────────────────────────────
    total_songs = db.query(func.count(Song.id)).filter(Song.band_id == band_id).scalar() or 0
    ready_songs = (
        db.query(func.count(Song.id))
        .filter(Song.band_id == band_id, Song.status == SongStatus.ready)
        .scalar() or 0
    )
    ready_pct = round((ready_songs / total_songs * 100) if total_songs > 0 else 0.0, 1)

    # ── Member count ──────────────────────────────────────────────────────────
    total_members = (
        db.query(func.count(BandMember.id)).filter(BandMember.band_id == band_id).scalar() or 0
    )

    # ── Upcoming sessions (next 5) ────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    upcoming = (
        db.query(RehearsalSession)
        .filter(
            RehearsalSession.band_id == band_id,
            RehearsalSession.status == SessionStatus.upcoming,
            RehearsalSession.scheduled_at >= now,
        )
        .order_by(RehearsalSession.scheduled_at.asc())
        .limit(5)
        .all()
    )
    upcoming_sessions = [
        SessionSummary(
            id=s.id,
            title=s.title,
            scheduled_at=s.scheduled_at,
            status=s.status,
            location=s.location,
        )
        for s in upcoming
    ]

    # ── Latest feedback (5 most recent) ──────────────────────────────────────
    latest_feedbacks_raw = (
        db.query(Feedback)
        .join(RehearsalSession, RehearsalSession.id == Feedback.session_id)
        .filter(RehearsalSession.band_id == band_id)
        .order_by(Feedback.created_at.desc())
        .limit(5)
        .all()
    )
    latest_feedbacks = [
        FeedbackSummary(
            id=f.id,
            content=f.content,
            created_at=f.created_at,
            username=f.user.username if f.user else None,
        )
        for f in latest_feedbacks_raw
    ]

    # ── Song progress summary (latest progress per song) ─────────────────────
    songs = db.query(Song).filter(Song.band_id == band_id).all()
    song_progress_summary = []
    for song in songs:
        latest = (
            db.query(SongProgress)
            .filter(SongProgress.song_id == song.id)
            .order_by(SongProgress.updated_at.desc())
            .first()
        )
        song_progress_summary.append(
            SongProgressSummary(
                song_id=song.id,
                song_title=song.title,
                latest_progress_pct=latest.progress_pct if latest else None,
            )
        )

    return DashboardResponse(
        total_songs=total_songs,
        ready_songs=ready_songs,
        ready_pct=ready_pct,
        total_members=total_members,
        upcoming_sessions=upcoming_sessions,
        latest_feedbacks=latest_feedbacks,
        song_progress_summary=song_progress_summary,
    )
