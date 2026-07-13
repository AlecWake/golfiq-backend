from typing import Literal

from pydantic import BaseModel, Field


EffectivenessLabel = Literal[
    "promising", "neutral", "struggling", "insufficient_data"
]
ConfidenceLabel = Literal["insufficient_data", "low", "moderate", "high"]


class PracticeTypeEffectivenessResult(BaseModel):
    practice_type: str
    practice_session_count: int = Field(ge=0)
    associated_round_count: int = Field(ge=0)
    average_associated_round_score: float | None = Field(default=None, ge=0)
    best_associated_round_score: int | None = Field(default=None, ge=0)
    worst_associated_round_score: int | None = Field(default=None, ge=0)
    score_difference: float | None
    effectiveness_label: EffectivenessLabel
    confidence_label: ConfidenceLabel
    observation: str


class PracticeTypeEffectivenessResponse(BaseModel):
    total_practice_types: int = Field(ge=0)
    total_practice_sessions_analyzed: int = Field(ge=0)
    total_rounds_analyzed: int = Field(ge=0)
    overall_average_score: float | None = Field(default=None, ge=0)
    lookback_days: int = Field(ge=1, le=90)
    minimum_rounds: int = Field(ge=1, le=20)
    results: list[PracticeTypeEffectivenessResult]
