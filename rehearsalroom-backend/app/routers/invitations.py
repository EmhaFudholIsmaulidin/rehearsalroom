from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_band_membership, require_band_leader
from app.models.user import User
from app.schemas.band import (
    InvitationCreateRequest, InvitationResponse,
    InvitationListResponse, AcceptInvitationRequest,
)
from app.schemas.band import BandMemberResponse
from app.services import band_service

router = APIRouter(tags=["Invitations"])


@router.post(
    "/bands/{band_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Kirim undangan via email (band_leader only)",
)
def create_invitation(
    band_id: UUID,
    data: InvitationCreateRequest,
    current_user: User = Depends(get_current_user),
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    return band_service.create_invitation(db, band_id, data, current_user)


@router.get(
    "/bands/{band_id}/invitations",
    response_model=InvitationListResponse,
    summary="List undangan pending",
)
def list_invitations(
    band_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    items, total = band_service.get_invitations(db, band_id, page, limit)
    return InvitationListResponse(items=items, total_count=total)


@router.delete(
    "/bands/{band_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Batalkan undangan",
)
def cancel_invitation(
    band_id: UUID,
    invitation_id: UUID,
    _membership=Depends(require_band_leader),
    db: Session = Depends(get_db),
):
    band_service.cancel_invitation(db, band_id, invitation_id)


@router.post(
    "/invitations/accept",
    response_model=BandMemberResponse,
    summary="Terima undangan via token",
)
def accept_invitation(
    data: AcceptInvitationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = band_service.accept_invitation(db, data.token, current_user)
    return BandMemberResponse(
        id=member.id,
        band_id=member.band_id,
        user_id=member.user_id,
        role=member.role,
        instrument=member.instrument,
        joined_at=member.joined_at,
        username=current_user.username,
        email=current_user.email,
    )
