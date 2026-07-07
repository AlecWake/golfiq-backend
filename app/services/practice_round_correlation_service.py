from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.practice_round_correlation import PracticeRoundCorrelationResponse


NOT_ENOUGH_DATA_OBSERVATION = "Not enough data yet."
BASIC_CORRELATION_OBSERVATION = (
    "You have logged practice and round data. "
    "More advanced correlation will be added later."
)


def _average(values: list[int]) -> float:
    if not values:
        return 0.0

    return round(sum(values) / len(values), 2)


def _most_common_practice_type(
    practice_sessions: list[PracticeSession],
) -> str | None:
    if not practice_sessions:
        return None

    counts: dict[str, int] = {}

    for practice_session in practice_sessions:
        practice_type = practice_session.practice_type
        counts[practice_type] = counts.get(practice_type, 0) + 1

    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def get_practice_round_correlation(
    db: Session,
    current_user: User,
) -> PracticeRoundCorrelationResponse:
    practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .all()
    )
    user_rounds = (
        db.query(Round)
        .filter(Round.user_id == current_user.id)
        .all()
    )

    practice_ratings = [
        practice_session.overall_rating
        for practice_session in practice_sessions
        if practice_session.overall_rating is not None
    ]
    practice_durations = [
        practice_session.duration_minutes
        for practice_session in practice_sessions
        if practice_session.duration_minutes is not None
    ]
    round_scores = [
        user_round.total_score
        for user_round in user_rounds
        if user_round.total_score is not None
    ]
    simple_observation = NOT_ENOUGH_DATA_OBSERVATION

    if practice_sessions and user_rounds:
        simple_observation = BASIC_CORRELATION_OBSERVATION

    return PracticeRoundCorrelationResponse(
        total_practice_sessions=len(practice_sessions),
        total_rounds=len(user_rounds),
        average_practice_rating=_average(practice_ratings),
        average_round_score=_average(round_scores),
        total_practice_minutes=sum(practice_durations),
        most_common_practice_type=_most_common_practice_type(practice_sessions),
        best_round_score=min(round_scores) if round_scores else None,
        worst_round_score=max(round_scores) if round_scores else None,
        simple_observation=simple_observation,
    )
