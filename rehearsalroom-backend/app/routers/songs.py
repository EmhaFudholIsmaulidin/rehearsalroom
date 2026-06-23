from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_band_membership, require_band_leader
from app.models.user import User
from app.schemas.song import (
    SongCreateRequest, SongUpdateRequest,
    SongStatusUpdateRequest, SongResponse, SongListResponse,
)
from app.services import song_service

router = APIRouter(prefix="/bands/{band_id}/songs", tags=["Songs"])


@router.get(
    "",
    response_model=SongListResponse,
    summary="List lagu band",
)
def get_songs(
    band_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    items, total = song_service.get_songs(db, band_id, page, limit)
    return SongListResponse(items=items, total_count=total)


@router.post(
    "",
    response_model=SongResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah lagu baru (band_leader only)",
)
def create_song(
    band_id: UUID,
    data: SongCreateRequest,
    current_user: User = Depends(get_current_user),
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return song_service.create_song(db, band_id, data, current_user)


@router.get(
    "/{song_id}",
    response_model=SongResponse,
    summary="Detail lagu",
)
def get_song(
    band_id: UUID,
    song_id: UUID,
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    return song_service.get_song(db, band_id, song_id)


@router.patch(
    "/{song_id}",
    response_model=SongResponse,
    summary="Edit lagu (band_leader only)",
)
def update_song(
    band_id: UUID,
    song_id: UUID,
    data: SongUpdateRequest,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return song_service.update_song(db, band_id, song_id, data)


@router.delete(
    "/{song_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus lagu (band_leader only)",
)
def delete_song(
    band_id: UUID,
    song_id: UUID,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    song_service.delete_song(db, band_id, song_id)


@router.patch(
    "/{song_id}/status",
    response_model=SongResponse,
    summary="Update status lagu (band_leader only)",
)
def update_song_status(
    band_id: UUID,
    song_id: UUID,
    data: SongStatusUpdateRequest,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return song_service.update_song_status(db, band_id, song_id, data.status)
