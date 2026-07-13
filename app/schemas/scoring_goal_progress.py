from typing import Literal

from pydantic import BaseModel, Field


GoalStatus = Literal[
    "no_goal",
    "unrecognized_goal",
    "insufficient_data",
    "not_yet_reached",
    "occasionally_reached",
    "consistently_reached",
]
TrendLabel = Literal["improving", "stable", "declining", "insufficient_data"]


class ScoringGoalProgressResponse(BaseModel):
    scoring_goal: str | None
    target_score: int | None = Field(default=None, gt=0)
    goal_status: GoalStatus
    total_rounds: int = Field(ge=0)
    recent_rounds_considered: int = Field(ge=0)
    current_average_score: float | None = Field(default=None, gt=0)
    recent_average_score: float | None = Field(default=None, gt=0)
    best_score: int | None = Field(default=None, gt=0)
    rounds_at_or_below_target: int = Field(ge=0)
    percentage_at_or_below_target: float = Field(ge=0, le=100)
    strokes_from_goal: float | None = None
    trend_label: TrendLabel
    observation: str
