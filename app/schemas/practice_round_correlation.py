from pydantic import BaseModel, Field


class PracticeRoundCorrelationResponse(BaseModel):
    total_practice_sessions: int = Field(ge=0)
    total_rounds: int = Field(ge=0)
    average_practice_rating: float = Field(ge=0)
    average_round_score: float = Field(ge=0)
    total_practice_minutes: int = Field(ge=0)
    most_common_practice_type: str | None
    best_round_score: int | None = Field(default=None, ge=0)
    worst_round_score: int | None = Field(default=None, ge=0)
    simple_observation: str
