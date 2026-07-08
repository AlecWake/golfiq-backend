from datetime import date

from pydantic import BaseModel

from app.schemas.recommendation import RecommendationResponse


class DashboardSummaryResponse(BaseModel):
    total_rounds: int
    total_practice_sessions: int
    total_clubs: int
    total_swing_thoughts: int
    most_recent_round_date: date | None
    most_recent_practice_session_date: date | None
    best_score: int | None
    average_score: float | None
    average_putts: float | None
    average_practice_rating: float | None
    total_recommendations: int
    highest_priority_recommendation: RecommendationResponse | None
