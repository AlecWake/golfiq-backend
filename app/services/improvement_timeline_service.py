from sqlalchemy.orm import Session, selectinload

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.improvement_timeline import ImprovementTimelineResponse
from app.services.round_analytics_service import (
    _fairway_percentage_for_round,
    _gir_percentage_for_round,
)


def _average_putts_for_round(user_round: Round) -> float | None:
    if user_round.stats is not None:
        return round(user_round.stats.putts / user_round.holes_played, 2)

    if user_round.hole_scores:
        putt_total = sum(hole_score.putts for hole_score in user_round.hole_scores)
        return round(putt_total / len(user_round.hole_scores), 2)

    return None


def _trend_label(current_score: int, previous_score: int | None) -> str:
    if previous_score is None:
        return "insufficient_data"

    if current_score < previous_score:
        return "improving"

    if current_score > previous_score:
        return "declining"

    return "stable"


def get_improvement_timeline(
    db: Session,
    current_user: User,
) -> ImprovementTimelineResponse:
    user_rounds = (
        db.query(Round)
        .options(selectinload(Round.stats), selectinload(Round.hole_scores))
        .filter(Round.user_id == current_user.id)
        .order_by(Round.round_date, Round.id)
        .all()
    )
    practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .order_by(PracticeSession.session_date, PracticeSession.id)
        .all()
    )

    timeline = []
    previous_round = None

    for user_round in user_rounds:
        if previous_round is None:
            practice_sessions_count = 0
            previous_score = None
        else:
            practice_sessions_count = sum(
                1
                for practice_session in practice_sessions
                if previous_round.round_date
                < practice_session.session_date
                <= user_round.round_date
            )
            previous_score = previous_round.total_score

        timeline.append(
            {
                "round_id": user_round.id,
                "round_date": user_round.round_date,
                "course_name": user_round.course_name,
                "total_score": user_round.total_score,
                "average_putts": _average_putts_for_round(user_round),
                "fairway_percentage": _fairway_percentage_for_round(user_round),
                "gir_percentage": _gir_percentage_for_round(user_round),
                "practice_sessions_since_previous_round": practice_sessions_count,
                "overall_trend_label": _trend_label(
                    user_round.total_score,
                    previous_score,
                ),
            }
        )
        previous_round = user_round

    return ImprovementTimelineResponse(timeline=timeline)
