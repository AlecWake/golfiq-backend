from datetime import timedelta

from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.swing_thought_effectiveness import SwingThoughtEffectivenessResult


MEANINGFUL_SCORE_DIFFERENCE = 1.0
MIN_ASSOCIATED_ROUNDS = 2

EFFECTIVENESS_SORT_ORDER = {
    "promising": 0,
    "neutral": 1,
    "struggling": 2,
    "insufficient_data": 3,
}


def _average_score(score_values: list[int]) -> float | None:
    if not score_values:
        return None

    return round(sum(score_values) / len(score_values), 2)


def _owned_practice_sessions(
    swing_thought_record: SwingThought,
) -> list[PracticeSession]:
    return [
        practice_session_record
        for practice_session_record in swing_thought_record.practice_sessions
        if practice_session_record.user_id == swing_thought_record.user_id
    ]


def _is_round_associated_with_practice(
    user_round: Round,
    practice_session_records: list[PracticeSession],
    lookback_days: int,
) -> bool:
    return any(
        practice_session_record.session_date
        < user_round.round_date
        <= practice_session_record.session_date + timedelta(days=lookback_days)
        for practice_session_record in practice_session_records
    )


def _associated_rounds(
    user_rounds: list[Round],
    swing_thought_record: SwingThought,
    lookback_days: int,
) -> list[Round]:
    associated_rounds_by_id: dict[int, Round] = {}
    practice_session_records = _owned_practice_sessions(swing_thought_record)

    for user_round in user_rounds:
        if _is_round_associated_with_practice(
            user_round,
            practice_session_records,
            lookback_days,
        ):
            associated_rounds_by_id[user_round.id] = user_round

    return sorted(
        associated_rounds_by_id.values(),
        key=lambda round_record: (round_record.round_date, round_record.id),
    )


def _effectiveness_label(
    associated_round_count: int,
    average_associated_round_score: float | None,
    overall_average_score: float | None,
) -> str:
    """Assign deterministic labels from round counts and a 1-stroke threshold."""
    if (
        associated_round_count < MIN_ASSOCIATED_ROUNDS
        or average_associated_round_score is None
        or overall_average_score is None
    ):
        return "insufficient_data"

    score_difference = average_associated_round_score - overall_average_score

    if score_difference <= -MEANINGFUL_SCORE_DIFFERENCE:
        return "promising"

    if score_difference >= MEANINGFUL_SCORE_DIFFERENCE:
        return "struggling"

    return "neutral"


def _confidence_label(associated_round_count: int) -> str:
    if associated_round_count < MIN_ASSOCIATED_ROUNDS:
        return "insufficient_data"

    if associated_round_count == 2:
        return "low"

    if associated_round_count <= 5:
        return "moderate"

    return "high"


def _observation(
    effectiveness_label: str,
    average_associated_round_score: float | None,
    overall_average_score: float | None,
) -> str:
    if (
        effectiveness_label == "insufficient_data"
        or average_associated_round_score is None
        or overall_average_score is None
    ):
        return "Not enough associated round data yet."

    score_difference = round(
        average_associated_round_score - overall_average_score,
        1,
    )

    if effectiveness_label == "promising":
        strokes_difference = abs(score_difference)
        return (
            "Rounds associated with this swing thought averaged "
            f"{strokes_difference:g} strokes lower than your overall average. "
            "This is an association and does not prove causation."
        )

    if effectiveness_label == "struggling":
        return (
            "Rounds associated with this swing thought averaged higher than "
            "your overall average. This is an association and does not prove "
            "causation."
        )

    return (
        "Rounds associated with this swing thought were similar to your "
        "overall scoring average."
    )


def _build_result(
    swing_thought_record: SwingThought,
    associated_round_records: list[Round],
    overall_average_score: float | None,
) -> SwingThoughtEffectivenessResult:
    associated_score_values = [
        round_record.total_score for round_record in associated_round_records
    ]
    average_associated_round_score = _average_score(associated_score_values)
    effectiveness_label = _effectiveness_label(
        len(associated_round_records),
        average_associated_round_score,
        overall_average_score,
    )

    return SwingThoughtEffectivenessResult(
        swing_thought_id=swing_thought_record.id,
        title=swing_thought_record.title,
        category=swing_thought_record.category,
        linked_practice_sessions=len(_owned_practice_sessions(swing_thought_record)),
        associated_rounds=len(associated_round_records),
        average_associated_round_score=average_associated_round_score,
        best_associated_round_score=(
            min(associated_score_values) if associated_score_values else None
        ),
        worst_associated_round_score=(
            max(associated_score_values) if associated_score_values else None
        ),
        effectiveness_label=effectiveness_label,
        confidence_label=_confidence_label(len(associated_round_records)),
        observation=_observation(
            effectiveness_label,
            average_associated_round_score,
            overall_average_score,
        ),
    )


def get_swing_thought_effectiveness(
    db: Session,
    current_user: User,
    lookback_days: int = 30,
) -> list[SwingThoughtEffectivenessResult]:
    swing_thought_records = (
        db.query(SwingThought)
        .filter(SwingThought.user_id == current_user.id)
        .order_by(SwingThought.title, SwingThought.id)
        .all()
    )
    user_rounds = (
        db.query(Round)
        .filter(Round.user_id == current_user.id)
        .order_by(Round.round_date, Round.id)
        .all()
    )
    overall_average_score = _average_score(
        [round_record.total_score for round_record in user_rounds]
    )

    results = [
        _build_result(
            swing_thought_record,
            _associated_rounds(user_rounds, swing_thought_record, lookback_days),
            overall_average_score,
        )
        for swing_thought_record in swing_thought_records
    ]

    return sorted(
        results,
        key=lambda result: (
            EFFECTIVENESS_SORT_ORDER[result.effectiveness_label],
            -result.associated_rounds,
            result.title.lower(),
            result.swing_thought_id,
        ),
    )
