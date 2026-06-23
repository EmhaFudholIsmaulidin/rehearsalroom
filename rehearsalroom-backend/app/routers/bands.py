from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_band_membership, require_band_leader
from app.models.user import User
from app.schemas.band import (
    BandCreateRequest, BandUpdateRequest,
    BandResponse, BandListResponse,
)
from app.services import band_service

router = APIRouter(prefix="/bands", tags=["Bands"])


@router.post(
    "",
    response_model=BandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat band baru (user otomatis jadi band_leader)",
)
def create_band(
    data: BandCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return band_service.create_band(db, data, current_user)


@router.get(
    "/my",
    response_model=BandListResponse,
    summary="List band yang diikuti user login",
)
def get_my_bands(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = band_service.get_bands_for_user(db, current_user.id, page, limit)
    return BandListResponse(items=items, total_count=total)


@router.get(
    "/{band_id}",
    response_model=BandResponse,
    summary="Detail band",
)
def get_band(
    band_id: UUID,
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    return band_service.get_band_by_id(db, band_id)


@router.patch(
    "/{band_id}",
    response_model=BandResponse,
    summary="Edit info band (band_leader only)",
)
def update_band(
    band_id: UUID,
    data: BandUpdateRequest,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return band_service.update_band(db, band_id, data)


@router.delete(
    "/{band_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus band (band_leader only)",
)
def delete_band(
    band_id: UUID,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    band_service.delete_band(db, band_id)
