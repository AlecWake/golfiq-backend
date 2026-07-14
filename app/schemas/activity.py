from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ActivityType(str, Enum):
    """Activity categories available when filtering the activity feed."""

    ALL = "all"
    ROUND = "round"
    PRACTICE = "practice"


class RoundActivityMetadata(BaseModel):
    course_name: str
    tee_box: str | None
    holes_played: int
    total_score: int


class PracticeActivityMetadata(BaseModel):
    practice_type: str
    duration_minutes: int | None
    overall_rating: int | None


class ActivityItemResponse(BaseModel):
    activity_type: Literal["round", "practice"]
    activity_id: int
    activity_date: date
    title: str
    summary: str
    created_at: datetime
    metadata: RoundActivityMetadata | PracticeActivityMetadata


class ActivityFeedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool
    items: list[ActivityItemResponse]
