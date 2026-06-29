from datetime import date, datetime

from pydantic import BaseModel, Field


class PracticeSessionCreateRequest(BaseModel):
    session_date: date
    practice_type: str = Field(min_length=1, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None
    overall_rating: int | None = Field(default=None, ge=1, le=10)


class PracticeSessionUpdateRequest(BaseModel):
    session_date: date | None = None
    practice_type: str | None = Field(default=None, min_length=1, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None
    overall_rating: int | None = Field(default=None, ge=1, le=10)


class PracticeSessionResponse(BaseModel):
    id: int
    user_id: int
    session_date: date
    practice_type: str
    duration_minutes: int | None
    notes: str | None
    overall_rating: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }