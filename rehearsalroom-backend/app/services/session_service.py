from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.session import RehearsalSession, SessionSong
from app.models.song import Song
from app.models.user import User
from app.schemas.session import SessionCreateRequest, SessionUpdateRequest


def create_session(db: Session, band_id: UUID, data: SessionCreateRequest, user: User) -> RehearsalSession:
    session = RehearsalSession(
        band_id=band_id,
        title=data.title,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
        location=data.location,
        created_by=user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions(db: Session, band_id: UUID, page: int, limit: int):
    query = (
        db.query(RehearsalSession)
        .filter(RehearsalSession.band_id == band_id)
        .order_by(RehearsalSession.scheduled_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def get_session(db: Session, band_id: UUID, session_id: UUID) -> RehearsalSession:
    session = (
        db.query(RehearsalSession)
        .options(
            joinedload(RehearsalSession.session_songs).joinedload(SessionSong.song),
            joinedload(RehearsalSession.progress_entries),
        )
        .filter(
            RehearsalSession.id == session_id,
            RehearsalSession.band_id == band_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesi latihan tidak ditemukan")
    return session


def get_session_or_404(db: Session, session_id: UUID) -> RehearsalSession:
    session = db.query(RehearsalSession).filter(RehearsalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesi latihan tidak ditemukan")
    return session


def update_session(
    db: Session, band_id: UUID, session_id: UUID, data: SessionUpdateRequest
) -> RehearsalSession:
    session = get_session(db, band_id, session_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


def update_session_status(db: Session, band_id: UUID, session_id: UUID, new_status) -> RehearsalSession:
    session = get_session(db, band_id, session_id)
    session.status = new_status
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, band_id: UUID, session_id: UUID) -> None:
    session = get_session(db, band_id, session_id)
    db.delete(session)
    db.commit()


# ── Session Songs ─────────────────────────────────────────────────────────────

def add_song_to_session(
    db: Session, session_id: UUID, song_id: UUID, order_index: Optional[int] = None
) -> SessionSong:
    # Check song not already in session
    existing = (
        db.query(SessionSong)
        .filter(SessionSong.session_id == session_id, SessionSong.song_id == song_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lagu sudah ada di sesi ini",
        )

    if order_index is None:
        # Auto-assign to end
        last = (
            db.query(SessionSong)
            .filter(SessionSong.session_id == session_id)
            .order_by(SessionSong.order_index.desc())
            .first()
        )
        order_index = (last.order_index + 1) if last else 0

    session_song = SessionSong(
        session_id=session_id,
        song_id=song_id,
        order_index=order_index,
    )
    db.add(session_song)
    db.commit()
    db.refresh(session_song)
    return session_song


def remove_song_from_session(db: Session, session_id: UUID, song_id: UUID) -> None:
    session_song = (
        db.query(SessionSong)
        .filter(SessionSong.session_id == session_id, SessionSong.song_id == song_id)
        .first()
    )
    if not session_song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lagu tidak ada di sesi ini",
        )
    db.delete(session_song)
    db.commit()


def reorder_session_songs(db: Session, session_id: UUID, song_orders: list[dict]) -> list[SessionSong]:
    results = []
    for item in song_orders:
        song_id = item.get("song_id")
        order_index = item.get("order_index")
        if song_id is None or order_index is None:
            continue
        session_song = (
            db.query(SessionSong)
            .filter(SessionSong.session_id == session_id, SessionSong.song_id == song_id)
            .first()
        )
        if session_song:
            session_song.order_index = order_index
            results.append(session_song)
    db.commit()
    for s in results:
        db.refresh(s)
    return results
