import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.band import Band, BandMember, Invitation, MemberRole, InvitationStatus
from app.models.user import User
from app.schemas.band import (
    BandCreateRequest, BandUpdateRequest,
    BandMemberUpdateRequest, InvitationCreateRequest,
)
from app.utils.email import send_invitation_email


# ── Band CRUD ─────────────────────────────────────────────────────────────────

def create_band(db: Session, data: BandCreateRequest, creator: User) -> Band:
    band = Band(
        name=data.name,
        genre=data.genre,
        formed_year=data.formed_year,
        created_by=creator.id,
    )
    db.add(band)
    db.flush()

    # Auto-add creator as band_leader
    membership = BandMember(
        band_id=band.id,
        user_id=creator.id,
        role=MemberRole.band_leader,
    )
    db.add(membership)
    db.commit()
    db.refresh(band)
    return band


def get_bands_for_user(db: Session, user_id: UUID, page: int, limit: int):
    query = (
        db.query(Band)
        .join(BandMember, BandMember.band_id == Band.id)
        .filter(BandMember.user_id == user_id)
    )
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def get_band_by_id(db: Session, band_id: UUID) -> Band:
    band = db.query(Band).filter(Band.id == band_id).first()
    if not band:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Band tidak ditemukan")
    return band


def update_band(db: Session, band_id: UUID, data: BandUpdateRequest) -> Band:
    band = get_band_by_id(db, band_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(band, field, value)
    db.commit()
    db.refresh(band)
    return band


def delete_band(db: Session, band_id: UUID) -> None:
    band = get_band_by_id(db, band_id)
    db.delete(band)
    db.commit()


# ── Members ───────────────────────────────────────────────────────────────────

def get_band_members(db: Session, band_id: UUID, page: int, limit: int):
    query = (
        db.query(BandMember)
        .options(joinedload(BandMember.user))
        .filter(BandMember.band_id == band_id)
    )
    total = query.count()
    members = query.offset((page - 1) * limit).limit(limit).all()
    return members, total


def remove_band_member(db: Session, band_id: UUID, user_id: UUID, current_user_id: UUID) -> None:
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kamu tidak bisa mengeluarkan diri sendiri",
        )
    member = (
        db.query(BandMember)
        .filter(BandMember.band_id == band_id, BandMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member tidak ditemukan")
    db.delete(member)
    db.commit()


def update_band_member(db: Session, band_id: UUID, user_id: UUID, data: BandMemberUpdateRequest) -> BandMember:
    member = (
        db.query(BandMember)
        .filter(BandMember.band_id == band_id, BandMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member tidak ditemukan")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


# ── Invitations ───────────────────────────────────────────────────────────────

def create_invitation(
    db: Session, band_id: UUID, data: InvitationCreateRequest, inviter: User
) -> Invitation:
    band = get_band_by_id(db, band_id)

    # Check if already a member
    existing_member = (
        db.query(BandMember)
        .join(User, User.id == BandMember.user_id)
        .filter(BandMember.band_id == band_id, User.email == data.invited_email)
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ini sudah menjadi anggota band",
        )

    # Check for pending invitation
    existing_inv = (
        db.query(Invitation)
        .filter(
            Invitation.band_id == band_id,
            Invitation.invited_email == data.invited_email,
            Invitation.status == InvitationStatus.pending,
        )
        .first()
    )
    if existing_inv:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Undangan pending sudah ada untuk email ini",
        )

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    invitation = Invitation(
        band_id=band_id,
        invited_email=data.invited_email,
        invited_by=inviter.id,
        token=token,
        expires_at=expires_at,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send email (non-blocking, stub if no SMTP configured)
    send_invitation_email(
        invited_email=data.invited_email,
        band_name=band.name,
        inviter_name=inviter.username,
        token=token,
    )

    return invitation


def get_invitations(db: Session, band_id: UUID, page: int, limit: int):
    query = db.query(Invitation).filter(
        Invitation.band_id == band_id,
        Invitation.status == InvitationStatus.pending,
    )
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def cancel_invitation(db: Session, band_id: UUID, invitation_id: UUID) -> None:
    invitation = (
        db.query(Invitation)
        .filter(Invitation.id == invitation_id, Invitation.band_id == band_id)
        .first()
    )
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Undangan tidak ditemukan")
    db.delete(invitation)
    db.commit()


def accept_invitation(db: Session, token: str, user: User) -> BandMember:
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token undangan tidak valid")

    if invitation.status != InvitationStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Undangan sudah tidak aktif",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = InvitationStatus.expired
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Undangan sudah kadaluarsa",
        )

    if invitation.invited_email.lower() != user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email tidak sesuai dengan undangan",
        )

    # Check not already member
    existing = (
        db.query(BandMember)
        .filter(BandMember.band_id == invitation.band_id, BandMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kamu sudah menjadi anggota band ini",
        )

    membership = BandMember(
        band_id=invitation.band_id,
        user_id=user.id,
        role=MemberRole.member,
    )
    db.add(membership)

    invitation.status = InvitationStatus.accepted
    db.commit()
    db.refresh(membership)
    return membership
