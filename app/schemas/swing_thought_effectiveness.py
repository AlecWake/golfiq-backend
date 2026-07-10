from typing import Literal

from pydantic import BaseModel, Field


SwingThoughtEffectivenessLabel = Literal[
    "promising",
    "neutral",
    "struggling",
    "insufficient_data",
]
SwingThoughtConfidenceLabel = Literal[
    "insufficient_data",
    "low",
    "moderate",
    "high",
]


class SwingThoughtEffectivenessResult(BaseModel):
    swing_thought_id: int
    title: str
    category: str | None
    linked_practice_sessions: int = Field(ge=0)
    associated_rounds: int = Field(ge=0)
    average_associated_round_score: float | None = Field(default=None, ge=0)
    best_associated_round_score: int | None = Field(default=None, ge=0)
    worst_associated_round_score: int | None = Field(default=None, ge=0)
    effectiveness_label: SwingThoughtEffectivenessLabel
    confidence_label: SwingThoughtConfidenceLabel
    observation: str
