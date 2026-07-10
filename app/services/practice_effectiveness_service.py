from datetime import timedelta

from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.practice_effectiveness import PracticeEffectivenessResponse


NOT_ENOUGH_COMPARISON_DATA_OBSERVATION = "Not enough comparison data yet."
NO_IMPROVEMENT_OBSERVATION = (
    "No scoring improvement was observed after recent practice in the current data."
)


def _average_score(scores: list[int]) -> float | None:
    if not scores:
        return None

    return round(sum(scores) / len(scores), 2)


def _score_difference(
    average_score_after_practice: float | None,
    average_score_without_recent_practice: float | None,
) -> float | None:
    if (
        average_score_after_practice is None
        or average_score_without_recent_practice is None
    ):
        return None

    return round(
        average_score_after_practice - average_score_without_recent_practice,
        2,
    )


def _confidence_label(
    rounds_after_practice_count: int,
    rounds_without_recent_practice_count: int,
) -> str:
    if rounds_after_practice_count == 0 or rounds_without_recent_practice_count == 0:
        return "insufficient_data"

    if rounds_after_practice_count < 3 or rounds_without_recent_practice_count < 3:
        return "low"

    return "moderate"


def _observation(score_difference: float | None) -> str:
    if score_difference is None:
        return NOT_ENOUGH_COMPARISON_DATA_OBSERVATION

    if score_difference < 0:
        strokes_difference = abs(score_difference)
        return (
            "Rounds following recent practice averaged "
            f"{strokes_difference:g} fewer strokes, but this does not prove "
            "practice caused the improvement."
        )

    return NO_IMPROVEMENT_OBSERVATION


def _had_recent_practice(
    user_round: Round,
    practice_sessions: list[PracticeSession],
    lookback_days: int,
) -> bool:
    lookback_start_date = user_round.round_date - timedelta(days=lookback_days)

    return any(
        lookback_start_date <= practice_session.session_date < user_round.round_date
        for practice_session in practice_sessions
    )


def get_practice_effectiveness(
    db: Session,
    current_user: User,
    lookback_days: int = 14,
) -> PracticeEffectivenessResponse:
    user_rounds = (
        db.query(Round)
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

    scores_after_practice: list[int] = []
    scores_without_recent_practice: list[int] = []

    for user_round in user_rounds:
        if _had_recent_practice(user_round, practice_sessions, lookback_days):
            scores_after_practice.append(user_round.total_score)
        else:
            scores_without_recent_practice.append(user_round.total_score)

    average_score_after_practice = _average_score(scores_after_practice)
    average_score_without_recent_practice = _average_score(
        scores_without_recent_practice
    )
    score_difference = _score_difference(
        average_score_after_practice,
        average_score_without_recent_practice,
    )
    confidence_label = _confidence_label(
        len(scores_after_practice),
        len(scores_without_recent_practice),
    )

    return PracticeEffectivenessResponse(
        total_rounds_analyzed=len(user_rounds),
        rounds_after_practice=len(scores_after_practice),
        rounds_without_recent_practice=len(scores_without_recent_practice),
        average_score_after_practice=average_score_after_practice,
        average_score_without_recent_practice=average_score_without_recent_practice,
        score_difference=score_difference,
        practice_appears_helpful=score_difference is not None and score_difference < 0,
        confidence_label=confidence_label,
        observation=_observation(score_difference),
    )
