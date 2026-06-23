from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_band_membership, require_band_leader
from app.models.user import User
from app.schemas.band import BandMemberListResponse, BandMemberResponse, BandMemberUpdateRequest
from app.services import band_service

router = APIRouter(prefix="/bands/{band_id}/members", tags=["Members"])


@router.get(
    "",
    response_model=BandMemberListResponse,
    summary="List anggota band",
)
def get_members(
    band_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _membership=Depends(get_band_membership),
    db: Session = Depends(get_db),
):
    members, total = band_service.get_band_members(db, band_id, page, limit)
    result = []
    for m in members:
        item = BandMemberResponse(
            id=m.id,
            band_id=m.band_id,
            user_id=m.user_id,
            role=m.role,
            instrument=m.instrument,
            joined_at=m.joined_at,
            username=m.user.username if m.user else None,
            email=m.user.email if m.user else None,
        )
        result.append(item)
    return BandMemberListResponse(items=result, total_count=total)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Keluarkan anggota dari band (band_leader only)",
)
def remove_member(
    band_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    band_service.remove_band_member(db, band_id, user_id, current_user.id)


@router.patch(
    "/{user_id}",
    response_model=BandMemberResponse,
    summary="Ubah role atau instrumen member (band_leader only)",
)
def update_member(
    band_id: UUID,
    user_id: UUID,
    data: BandMemberUpdateRequest,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    member = band_service.update_band_member(db, band_id, user_id, data)
    return BandMemberResponse(
        id=member.id,
        band_id=member.band_id,
        user_id=member.user_id,
        role=member.role,
        instrument=member.instrument,
        joined_at=member.joined_at,
        username=member.user.username if member.user else None,
        email=member.user.email if member.user else None,
    )
