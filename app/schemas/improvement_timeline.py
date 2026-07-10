from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


OverallTrendLabel = Literal[
    "improving",
    "stable",
    "declining",
    "insufficient_data",
]


class ImprovementTimelineEntry(BaseModel):
    round_id: int
    round_date: date
    course_name: str
    total_score: int = Field(ge=0)
    average_putts: float | None = Field(default=None, ge=0)
    fairway_percentage: float | None = Field(default=None, ge=0)
    gir_percentage: float | None = Field(default=None, ge=0)
    practice_sessions_since_previous_round: int = Field(ge=0)
    overall_trend_label: OverallTrendLabel


class ImprovementTimelineResponse(BaseModel):
    timeline: list[ImprovementTimelineEntry]
