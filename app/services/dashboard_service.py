from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.club import Club
from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.round_stat import RoundStat
from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import get_user_recommendations


PRIORITY_RANK = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def _round_optional_average(value: Decimal | float | None) -> float | None:
    if value is None:
        return None

    return round(float(value), 2)


def _highest_priority_recommendation(
    recommendations: list[RecommendationResponse],
) -> RecommendationResponse | None:
    if not recommendations:
        return None

    return max(
        recommendations,
        key=lambda recommendation: PRIORITY_RANK[recommendation.priority],
    )


def get_dashboard_summary(
    db: Session,
    current_user: User,
) -> DashboardSummaryResponse:
    total_rounds = (
        db.query(Round)
        .filter(Round.user_id == current_user.id)
        .count()
    )
    total_practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .count()
    )
    total_clubs = (
        db.query(Club)
        .filter(Club.user_id == current_user.id)
        .count()
    )
    total_swing_thoughts = (
        db.query(SwingThought)
        .filter(SwingThought.user_id == current_user.id)
        .count()
    )

    most_recent_round_date: date | None = (
        db.query(func.max(Round.round_date))
        .filter(Round.user_id == current_user.id)
        .scalar()
    )
    most_recent_practice_session_date: date | None = (
        db.query(func.max(PracticeSession.session_date))
        .filter(PracticeSession.user_id == current_user.id)
        .scalar()
    )
    best_score: int | None = (
        db.query(func.min(Round.total_score))
        .filter(Round.user_id == current_user.id)
        .scalar()
    )
    average_score = (
        db.query(func.avg(Round.total_score))
        .filter(Round.user_id == current_user.id)
        .scalar()
    )
    average_putts = (
        db.query(func.avg(RoundStat.putts))
        .join(Round, Round.id == RoundStat.round_id)
        .filter(Round.user_id == current_user.id)
        .scalar()
    )
    average_practice_rating = (
        db.query(func.avg(PracticeSession.overall_rating))
        .filter(
            PracticeSession.user_id == current_user.id,
            PracticeSession.overall_rating.is_not(None),
        )
        .scalar()
    )

    recommendations = get_user_recommendations(db, current_user)

    return DashboardSummaryResponse(
        total_rounds=total_rounds,
        total_practice_sessions=total_practice_sessions,
        total_clubs=total_clubs,
        total_swing_thoughts=total_swing_thoughts,
        most_recent_round_date=most_recent_round_date,
        most_recent_practice_session_date=most_recent_practice_session_date,
        best_score=best_score,
        average_score=_round_optional_average(average_score),
        average_putts=_round_optional_average(average_putts),
        average_practice_rating=_round_optional_average(average_practice_rating),
        total_recommendations=len(recommendations),
        highest_priority_recommendation=_highest_priority_recommendation(
            recommendations,
        ),
    )
