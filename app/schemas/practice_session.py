from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PracticeSessionCreateRequest(BaseModel):
    session_date: date = Field(
        description="Calendar date of the practice session.",
        examples=["2026-07-12"],
    )
    practice_type: str = Field(
        min_length=1,
        max_length=100,
        description="Primary practice focus.",
        examples=["Putting"],
    )
    duration_minutes: int | None = Field(
        default=None,
        ge=0,
        description="Session duration in minutes.",
        examples=[45],
    )
    notes: str | None = Field(
        default=None,
        description="Optional free-form practice notes.",
        examples=["Worked on start line from six feet."],
    )
    overall_rating: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Subjective session quality from 1 to 10.",
        examples=[8],
    )

    model_config = ConfigDict(title="Practice Session Creation Request")


class PracticeSessionUpdateRequest(BaseModel):
    session_date: date | None = None
    practice_type: str | None = Field(default=None, min_length=1, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None
    overall_rating: int | None = Field(default=None, ge=1, le=10)

    model_config = ConfigDict(title="Practice Session Update Request")


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

    model_config = ConfigDict(from_attributes=True)
