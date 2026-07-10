from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLabel = Literal["insufficient_data", "low", "moderate"]


class PracticeEffectivenessResponse(BaseModel):
    total_rounds_analyzed: int = Field(ge=0)
    rounds_after_practice: int = Field(ge=0)
    rounds_without_recent_practice: int = Field(ge=0)
    average_score_after_practice: float | None = Field(default=None, ge=0)
    average_score_without_recent_practice: float | None = Field(default=None, ge=0)
    score_difference: float | None
    practice_appears_helpful: bool
    confidence_label: ConfidenceLabel
    observation: str
