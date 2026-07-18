from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RoundCreateRequest(BaseModel):
    round_date: date = Field(
        description="Calendar date the round was played.",
        examples=["2026-07-10"],
    )
    course_name: str = Field(
        min_length=1,
        max_length=150,
        description="Name of the golf course.",
        examples=["Pine Valley Municipal"],
    )
    tee_box: str | None = Field(
        default=None,
        description="Tee markers used for the round.",
        examples=["Blue"],
    )
    holes_played: Literal[9, 18] = Field(
        description="Number of holes completed.",
        examples=[18],
    )
    total_score: int = Field(
        gt=0,
        description="Total strokes recorded for the round.",
        examples=[88],
    )
    notes: str | None = Field(
        default=None,
        description="Optional free-form round notes.",
        examples=["Drove the ball well; lost strokes around the green."],
    )

    model_config = ConfigDict(title="Round Creation Request")


class RoundUpdateRequest(BaseModel):
    round_date: date | None = None
    course_name: str | None = Field(default=None, min_length=1, max_length=150)
    tee_box: str | None = None
    holes_played: Literal[9, 18] | None = None
    total_score: int | None = Field(default=None, gt=0)
    notes: str | None = None

    model_config = ConfigDict(title="Round Update Request")


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

    model_config = ConfigDict(from_attributes=True)
