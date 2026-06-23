from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_band_leader
from app.models.user import User
from app.models.band import BandMember
from app.models.session import RehearsalSession, SessionSong
from app.schemas.session import (
    AddSongToSessionRequest, ReorderSessionSongsRequest, SessionSongResponse,
)
from app.schemas.song import SongResponse
from app.services import session_service

router = APIRouter(prefix="/sessions/{session_id}/songs", tags=["Session Songs"])


def _get_session_and_check_leader(
    session_id: UUID,
    current_user: User,
    db: Session,
) -> tuple[RehearsalSession, BandMember]:
    """Get session and verify current user is band_leader for that band."""
    session = session_service.get_session_or_404(db, session_id)
    from app.models.band import MemberRole
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
    if membership.role != MemberRole.band_leader:
        raise HTTPException(status_code=403, detail="Hanya band leader yang bisa mengatur lagu dalam sesi")
    return session, membership


@router.post(
    "",
    response_model=SessionSongResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah lagu ke sesi (band_leader only)",
)
def add_song_to_session(
    session_id: UUID,
    data: AddSongToSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_session_and_check_leader(session_id, current_user, db)
    session_song = session_service.add_song_to_session(
        db, session_id, data.song_id, data.order_index
    )
    return SessionSongResponse(
        id=session_song.id,
        session_id=session_song.session_id,
        song_id=session_song.song_id,
        order_index=session_song.order_index,
        song=SongResponse.model_validate(session_song.song) if session_song.song else None,
    )


@router.delete(
    "/{song_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus lagu dari sesi (band_leader only)",
)
def remove_song_from_session(
    session_id: UUID,
    song_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_session_and_check_leader(session_id, current_user, db)
    session_service.remove_song_from_session(db, session_id, song_id)


@router.patch(
    "/reorder",
    response_model=list[SessionSongResponse],
    summary="Ubah urutan lagu dalam sesi (band_leader only)",
)
def reorder_songs(
    session_id: UUID,
    data: ReorderSessionSongsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_session_and_check_leader(session_id, current_user, db)
    session_songs = session_service.reorder_session_songs(db, session_id, data.song_orders)
    return [
        SessionSongResponse(
            id=ss.id,
            session_id=ss.session_id,
            song_id=ss.song_id,
            order_index=ss.order_index,
            song=SongResponse.model_validate(ss.song) if ss.song else None,
        )
        for ss in session_songs
    ]
