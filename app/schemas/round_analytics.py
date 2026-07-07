from pydantic import BaseModel, Field


class RoundAnalyticsSummaryResponse(BaseModel):
    round_id: int
    total_score: int = Field(ge=0)
    holes_played: int = Field(ge=0)
    fairways_hit: int = Field(ge=0)
    fairways_possible: int = Field(ge=0)
    fairway_percentage: float = Field(ge=0)
    greens_in_regulation: int = Field(ge=0)
    gir_percentage: float = Field(ge=0)
    total_putts: int = Field(ge=0)
    penalty_strokes: int = Field(ge=0)
    average_score_per_hole: float = Field(ge=0)
    birdies: int = Field(ge=0)
    pars: int = Field(ge=0)
    bogeys: int = Field(ge=0)
    double_bogeys_or_worse: int = Field(ge=0)


class MultiRoundAnalyticsSummaryResponse(BaseModel):
    total_rounds: int = Field(ge=0)
    average_score: float = Field(ge=0)
    best_score: int | None = Field(default=None, ge=0)
    worst_score: int | None = Field(default=None, ge=0)
    average_putts: float = Field(ge=0)
    average_penalties: float = Field(ge=0)
    average_fairway_percentage: float = Field(ge=0)
    average_gir_percentage: float = Field(ge=0)
    total_holes_played: int = Field(ge=0)
    recent_rounds_count: int = Field(ge=0)
