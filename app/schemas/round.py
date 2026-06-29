from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class RoundCreateRequest(BaseModel):
    round_date: date
    course_name: str = Field(min_length=1, max_length=150)
    tee_box: str | None = None
    holes_played: Literal[9, 18]
    total_score: int = Field(gt=0)
    notes: str | None = None


class RoundUpdateRequest(BaseModel):
    round_date: date | None = None
    course_name: str | None = Field(default=None, min_length=1, max_length=150)
    tee_box: str | None = None
    holes_played: Literal[9, 18] | None = None
    total_score: int | None = Field(default=None, gt=0)
    notes: str | None = None


class RoundResponse(BaseModel):
    id: int
    user_id: int
    round_date: date
    course_name: str
    tee_box: str | None
    holes_played: int
    total_score: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
