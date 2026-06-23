from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FeedbackCreateRequest(BaseModel):
    content: str


class FeedbackResponse(BaseModel):
    id: UUID
    session_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    username: Optional[str] = None

    model_config = {"from_attributes": True}


class FeedbackListResponse(BaseModel):
    items: list[FeedbackResponse]
    total_count: int
