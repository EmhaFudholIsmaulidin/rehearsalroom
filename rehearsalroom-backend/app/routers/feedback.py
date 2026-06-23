from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies import get_current_user
from app.models.band import BandMember, MemberRole
from app.models.session import RehearsalSession
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback import (
    FeedbackCreateRequest, FeedbackResponse, FeedbackListResponse,
)
from app.services import session_service

router = APIRouter(prefix="/sessions/{session_id}/feedback", tags=["Feedback"])


def _verify_and_get_membership(
    session_id: UUID,
    current_user: User,
    db: Session,
) -> tuple[RehearsalSession, BandMember]:
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
    return session, membership


@router.get(
    "",
    response_model=FeedbackListResponse,
    summary="List feedback sesi (band_leader lihat semua, member lihat milik sendiri)",
)
def get_feedback(
    session_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, membership = _verify_and_get_membership(session_id, current_user, db)

    query = (
        db.query(Feedback)
        .options(joinedload(Feedback.user))
        .filter(Feedback.session_id == session_id)
    )

    # Members only see their own feedback
    if membership.role != MemberRole.band_leader:
        query = query.filter(Feedback.user_id == current_user.id)

    total = query.count()
    items = query.order_by(Feedback.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    result = [
        FeedbackResponse(
            id=f.id,
            session_id=f.session_id,
            user_id=f.user_id,
            content=f.content,
            created_at=f.created_at,
            username=f.user.username if f.user else None,
        )
        for f in items
    ]
    return FeedbackListResponse(items=result, total_count=total)


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah feedback ke sesi (semua member bisa)",
)
def create_feedback(
    session_id: UUID,
    data: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_and_get_membership(session_id, current_user, db)

    feedback = Feedback(
        session_id=session_id,
        user_id=current_user.id,
        content=data.content,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse(
        id=feedback.id,
        session_id=feedback.session_id,
        user_id=feedback.user_id,
        content=feedback.content,
        created_at=feedback.created_at,
        username=current_user.username,
    )


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus feedback milik sendiri",
)
def delete_feedback(
    session_id: UUID,
    feedback_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    feedback = (
        db.query(Feedback)
        .filter(Feedback.id == feedback_id, Feedback.session_id == session_id)
        .first()
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback tidak ditemukan")
    if feedback.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kamu hanya bisa menghapus feedback milikmu sendiri")
    db.delete(feedback)
    db.commit()
