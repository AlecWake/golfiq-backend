from pydantic import BaseModel, Field


class PracticeAnalyticsSummaryResponse(BaseModel):
    total_practice_sessions: int = Field(ge=0)
    total_practice_minutes: int = Field(ge=0)
    average_session_duration: float = Field(ge=0)
    average_rating: float = Field(ge=0)
    practice_type_counts: dict[str, int]
    most_common_practice_type: str | None
    recent_sessions_count: int = Field(ge=0)
    active_swing_thoughts_count: int = Field(ge=0)
