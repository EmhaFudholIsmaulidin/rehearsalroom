from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.song import Song, SongProgress
from app.models.user import User
from app.schemas.song import SongCreateRequest, SongUpdateRequest, SongProgressCreateRequest


def create_song(db: Session, band_id: UUID, data: SongCreateRequest, user: User) -> Song:
    song = Song(
        band_id=band_id,
        title=data.title,
        composer=data.composer,
        duration_seconds=data.duration_seconds,
        status=data.status,
        added_by=user.id,
    )
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


def get_songs(db: Session, band_id: UUID, page: int, limit: int):
    query = db.query(Song).filter(Song.band_id == band_id).order_by(Song.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def get_song(db: Session, band_id: UUID, song_id: UUID) -> Song:
    song = db.query(Song).filter(Song.id == song_id, Song.band_id == band_id).first()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lagu tidak ditemukan")
    return song


def update_song(db: Session, band_id: UUID, song_id: UUID, data: SongUpdateRequest) -> Song:
    song = get_song(db, band_id, song_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(song, field, value)
    db.commit()
    db.refresh(song)
    return song


def update_song_status(db: Session, band_id: UUID, song_id: UUID, new_status) -> Song:
    song = get_song(db, band_id, song_id)
    song.status = new_status
    db.commit()
    db.refresh(song)
    return song


def delete_song(db: Session, band_id: UUID, song_id: UUID) -> None:
    song = get_song(db, band_id, song_id)
    db.delete(song)
    db.commit()


# ── Song Progress ─────────────────────────────────────────────────────────────

def get_session_progress(db: Session, session_id: UUID, page: int, limit: int):
    query = (
        db.query(SongProgress)
        .filter(SongProgress.session_id == session_id)
        .order_by(SongProgress.updated_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def upsert_song_progress(
    db: Session,
    session_id: UUID,
    data: SongProgressCreateRequest,
    user: User,
) -> SongProgress:
    # Check for existing progress entry for this session+song
    existing = (
        db.query(SongProgress)
        .filter(
            SongProgress.session_id == session_id,
            SongProgress.song_id == data.song_id,
        )
        .first()
    )

    if existing:
        existing.progress_pct = data.progress_pct
        existing.notes = data.notes
        existing.updated_by = user.id
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        progress = SongProgress(
            session_id=session_id,
            song_id=data.song_id,
            updated_by=user.id,
            progress_pct=data.progress_pct,
            notes=data.notes,
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress
