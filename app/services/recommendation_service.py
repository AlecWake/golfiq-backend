from datetime import date

from sqlalchemy.orm import Session, selectinload

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.recommendation import RecommendationResponse
from app.services.round_analytics_service import (
    _fairway_percentage_for_round,
    _gir_percentage_for_round,
    _stat_values_for_round,
)


RECENT_ACTIVITY_DAYS = 30


def _average(values: list[float | int]) -> float:
    if not values:
        return 0.0

    return round(sum(values) / len(values), 2)


def _add_recommendation(
    recommendations: list[RecommendationResponse],
    category: str,
    priority: str,
    title: str,
    description: str,
) -> None:
    recommendations.append(
        RecommendationResponse(
            recommendation_id=f"rec-{len(recommendations) + 1}",
            category=category,
            priority=priority,
            title=title,
            description=description,
        )
    )


def _latest_activity_date(
    practice_sessions: list[PracticeSession],
    rounds: list[Round],
) -> date | None:
    activity_dates = [
        practice_session.session_date for practice_session in practice_sessions
    ]
    activity_dates.extend(user_round.round_date for user_round in rounds)

    if not activity_dates:
        return None

    return max(activity_dates)


def _add_practice_recommendations(
    recommendations: list[RecommendationResponse],
    practice_sessions: list[PracticeSession],
    rounds: list[Round],
) -> None:
    latest_date = _latest_activity_date(practice_sessions, rounds)

    if not practice_sessions:
        _add_recommendation(
            recommendations,
            "Practice",
            "medium",
            "Log your first practice session",
            "You have not logged a practice session yet. Add one after your next range, short game, or putting session.",
        )
        return

    latest_session_date = max(
        practice_session.session_date for practice_session in practice_sessions
    )

    if (
        latest_date is not None
        and (latest_date - latest_session_date).days > RECENT_ACTIVITY_DAYS
    ):
        _add_recommendation(
            recommendations,
            "Practice",
            "medium",
            "Refresh your practice routine",
            "You have not logged a practice session recently. Schedule a focused session and track what you worked on.",
        )


def _add_swing_thought_recommendations(
    recommendations: list[RecommendationResponse],
    active_swing_thoughts_count: int,
) -> None:
    if active_swing_thoughts_count == 0:
        _add_recommendation(
            recommendations,
            "General",
            "low",
            "Create an active swing thought",
            "You have no active swing thoughts. Add one simple cue to bring into practice or your next round.",
        )


def _add_round_recommendations(
    recommendations: list[RecommendationResponse],
    rounds: list[Round],
) -> None:
    if not rounds:
        _add_recommendation(
            recommendations,
            "General",
            "low",
            "Log a round when you play",
            "Rounds help GolfIQ connect your practice habits to on-course results.",
        )
        return

    scores = [user_round.total_score for user_round in rounds]
    putt_totals: list[int] = []
    penalty_totals: list[int] = []
    fairway_percentages: list[float] = []
    gir_percentages: list[float] = []

    for user_round in rounds:
        putts, penalties = _stat_values_for_round(user_round)
        fairway_percentage = _fairway_percentage_for_round(user_round)
        gir_percentage = _gir_percentage_for_round(user_round)

        if putts is not None:
            putt_totals.append(putts)
        if penalties is not None:
            penalty_totals.append(penalties)
        if fairway_percentage is not None:
            fairway_percentages.append(fairway_percentage)
        if gir_percentage is not None:
            gir_percentages.append(gir_percentage)

    if _average(putt_totals) > 36:
        _add_recommendation(
            recommendations,
            "Putting",
            "high",
            "Prioritize putting practice",
            "You average more than 36 putts per round. Spend more time practicing distance control and short putts.",
        )

    if gir_percentages and _average(gir_percentages) < 35:
        _add_recommendation(
            recommendations,
            "Ball Striking",
            "high",
            "Practice approach shots",
            "Your GIR percentage is low. Consider practicing iron approach shots and wedge control.",
        )

    if fairway_percentages and _average(fairway_percentages) < 45:
        _add_recommendation(
            recommendations,
            "Accuracy",
            "medium",
            "Tighten tee shot accuracy",
            "Your fairway percentage is low. Spend practice time on tee shots that keep the ball in play.",
        )

    if _average(penalty_totals) >= 2:
        _add_recommendation(
            recommendations,
            "Penalties",
            "high",
            "Reduce penalty strokes",
            "Penalty strokes are adding up. Choose safer targets and club selections when trouble is in play.",
        )

    if len(scores) >= 3 and max(scores) - min(scores) >= 15:
        _add_recommendation(
            recommendations,
            "Consistency",
            "medium",
            "Build more consistent scoring",
            "Your scores vary by 15 or more shots. Track what changes between your best and hardest rounds.",
        )


def get_user_recommendations(
    db: Session,
    current_user: User,
) -> list[RecommendationResponse]:
    practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .all()
    )
    rounds = (
        db.query(Round)
        .options(selectinload(Round.stats), selectinload(Round.hole_scores))
        .filter(Round.user_id == current_user.id)
        .all()
    )
    active_swing_thoughts_count = (
        db.query(SwingThought)
        .filter(
            SwingThought.user_id == current_user.id,
            SwingThought.is_active.is_(True),
        )
        .count()
    )
    recommendations: list[RecommendationResponse] = []

    _add_practice_recommendations(recommendations, practice_sessions, rounds)
    _add_swing_thought_recommendations(
        recommendations,
        active_swing_thoughts_count,
    )
    _add_round_recommendations(recommendations, rounds)

    if not recommendations:
        _add_recommendation(
            recommendations,
            "General",
            "low",
            "Keep building your golf history",
            "Keep practicing. More data will improve recommendations.",
        )

    return recommendations
