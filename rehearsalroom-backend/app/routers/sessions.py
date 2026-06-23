from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_band_membership, require_band_leader
from app.models.user import User
from app.schemas.session import (
    SessionCreateRequest, SessionUpdateRequest,
    SessionStatusUpdateRequest, SessionResponse,
    SessionDetailResponse, SessionListResponse,
    SessionSongResponse,
)
from app.schemas.song import SongResponse, SongProgressResponse
from app.services import session_service

router = APIRouter(prefix="/bands/{band_id}/sessions", tags=["Sessions"])


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List sesi latihan band",
)
def get_sessions(
    band_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    items, total = session_service.get_sessions(db, band_id, page, limit)
    return SessionListResponse(items=items, total_count=total)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat sesi latihan baru (band_leader only)",
)
def create_session(
    band_id: UUID,
    data: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return session_service.create_session(db, band_id, data, current_user)


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="Detail sesi + lagu + progres",
)
def get_session(
    band_id: UUID,
    session_id: UUID,
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    session = session_service.get_session(db, band_id, session_id)

    session_songs = [
        SessionSongResponse(
            id=ss.id,
            session_id=ss.session_id,
            song_id=ss.song_id,
            order_index=ss.order_index,
            song=SongResponse.model_validate(ss.song) if ss.song else None,
        )
        for ss in session.session_songs
    ]

    progress_entries = [
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
        for p in session.progress_entries
    ]

    return SessionDetailResponse(
        id=session.id,
        band_id=session.band_id,
        title=session.title,
        scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes,
        location=session.location,
        status=session.status,
        created_by=session.created_by,
        created_at=session.created_at,
        session_songs=session_songs,
        progress_entries=progress_entries,
    )


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Edit sesi latihan (band_leader only)",
)
def update_session(
    band_id: UUID,
    session_id: UUID,
    data: SessionUpdateRequest,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return session_service.update_session(db, band_id, session_id, data)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus sesi latihan (band_leader only)",
)
def delete_session(
    band_id: UUID,
    session_id: UUID,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    session_service.delete_session(db, band_id, session_id)


@router.patch(
    "/{session_id}/status",
    response_model=SessionResponse,
    summary="Update status sesi (band_leader only)",
)
def update_session_status(
    band_id: UUID,
    session_id: UUID,
    data: SessionStatusUpdateRequest,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return session_service.update_session_status(db, band_id, session_id, data.status)
