from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_band_membership
from app.models.user import User
from app.models.band import BandMember
from app.models.session import RehearsalSession
from app.schemas.song import (
    SongProgressCreateRequest, SongProgressResponse, SongProgressListResponse,
)
from app.services import song_service, session_service

router = APIRouter(prefix="/sessions/{session_id}/progress", tags=["Song Progress"])


def _verify_session_membership(
    session_id: UUID,
    current_user: User,
    db: Session,
) -> RehearsalSession:
    """Verify user is a member of the band that owns this session."""
    session = session_service.get_session_or_404(db, session_id)
    membership = (
        db.query(BandMember)
        .filter(
            BandMember.band_id == session.band_id,
            BandMember.user_id == current_user.id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Kamu bukan anggota band ini")
    return session


@router.get(
    "",
    response_model=SongProgressListResponse,
    summary="List progres semua lagu dalam sesi",
)
def get_progress(
    session_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_session_membership(session_id, current_user, db)
    items, total = song_service.get_session_progress(db, session_id, page, limit)
    result = [
        SongProgressResponse(
            id=p.id,
            session_id=p.session_id,
            song_id=p.song_id,
            updated_by=p.updated_by,
            progress_pct=p.progress_pct,
            notes=p.notes,
            updated_at=p.updated_at,
            song_title=p.song.title if p.song else None,
        )
        for p in items
    ]
    return SongProgressListResponse(items=result, total_count=total)


@router.post(
    "",
    response_model=SongProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Buat atau update progres lagu (semua member bisa)",
)
def upsert_progress(
    session_id: UUID,
    data: SongProgressCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_session_membership(session_id, current_user, db)
    progress = song_service.upsert_song_progress(db, session_id, data, current_user)
    return SongProgressResponse(
        id=progress.id,
        session_id=progress.session_id,
        song_id=progress.song_id,
        updated_by=progress.updated_by,
        progress_pct=progress.progress_pct,
        notes=progress.notes,
        updated_at=progress.updated_at,
        song_title=progress.song.title if progress.song else None,
    )
