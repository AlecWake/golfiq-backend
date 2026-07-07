from datetime import timedelta

from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.practice_analytics import PracticeAnalyticsSummaryResponse


def _average(values: list[int]) -> float:
    if not values:
        return 0.0

    return round(sum(values) / len(values), 2)


def _practice_type_counts(
    practice_sessions: list[PracticeSession],
) -> dict[str, int]:
    counts: dict[str, int] = {}

    for practice_session in practice_sessions:
        practice_type = practice_session.practice_type
        counts[practice_type] = counts.get(practice_type, 0) + 1

    return counts


def _most_common_practice_type(counts: dict[str, int]) -> str | None:
    if not counts:
        return None

    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def get_practice_analytics_summary(
    db: Session,
    current_user: User,
) -> PracticeAnalyticsSummaryResponse:
    practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
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

    if not practice_sessions:
        return PracticeAnalyticsSummaryResponse(
            total_practice_sessions=0,
            total_practice_minutes=0,
            average_session_duration=0.0,
            average_rating=0.0,
            practice_type_counts={},
            most_common_practice_type=None,
            recent_sessions_count=0,
            active_swing_thoughts_count=active_swing_thoughts_count,
        )

    durations = [
        practice_session.duration_minutes
        for practice_session in practice_sessions
        if practice_session.duration_minutes is not None
    ]
    ratings = [
        practice_session.overall_rating
        for practice_session in practice_sessions
        if practice_session.overall_rating is not None
    ]
    practice_type_counts = _practice_type_counts(practice_sessions)
    latest_session_date = max(
        practice_session.session_date for practice_session in practice_sessions
    )
    recent_cutoff = latest_session_date - timedelta(days=30)
    recent_sessions_count = sum(
        1
        for practice_session in practice_sessions
        if practice_session.session_date >= recent_cutoff
    )

    return PracticeAnalyticsSummaryResponse(
        total_practice_sessions=len(practice_sessions),
        total_practice_minutes=sum(durations),
        average_session_duration=_average(durations),
        average_rating=_average(ratings),
        practice_type_counts=practice_type_counts,
        most_common_practice_type=_most_common_practice_type(practice_type_counts),
        recent_sessions_count=recent_sessions_count,
        active_swing_thoughts_count=active_swing_thoughts_count,
    )
