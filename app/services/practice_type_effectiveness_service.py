from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.practice_type_effectiveness import (
    PracticeTypeEffectivenessResponse,
    PracticeTypeEffectivenessResult,
)


MEANINGFUL_SCORE_DIFFERENCE = 1.0


def _normalize_practice_type(practice_type_name: str) -> str | None:
    normalized_name = " ".join(practice_type_name.strip().split()).casefold()
    return normalized_name or None


def _display_practice_type(normalized_name: str) -> str:
    return normalized_name.title()


def _average_score(scores: list[int]) -> float | None:
    if not scores:
        return None
    return round(sum(scores) / len(scores), 2)


def _effectiveness_label(
    associated_round_count: int,
    minimum_rounds: int,
    score_difference: float | None,
) -> str:
    if associated_round_count < minimum_rounds or score_difference is None:
        return "insufficient_data"
    if score_difference <= -MEANINGFUL_SCORE_DIFFERENCE:
        return "promising"
    if score_difference >= MEANINGFUL_SCORE_DIFFERENCE:
        return "struggling"
    return "neutral"


def _confidence_label(associated_round_count: int, minimum_rounds: int) -> str:
    if associated_round_count < minimum_rounds:
        return "insufficient_data"
    if associated_round_count < 4:
        return "low"
    if associated_round_count < 8:
        return "moderate"
    return "high"


def _observation(
    display_name: str,
    effectiveness_label: str,
    score_difference: float | None,
) -> str:
    practice_name = display_name.lower()
    if effectiveness_label == "insufficient_data":
        return "Not enough associated round data to evaluate this practice type."
    if effectiveness_label == "promising":
        return (
            f"Rounds following {practice_name} practice averaged "
            f"{abs(score_difference or 0):g} strokes lower than your overall "
            "average. This association does not prove that the practice caused "
            "the improvement."
        )
    if effectiveness_label == "struggling":
        return (
            f"Rounds following {practice_name} practice averaged "
            f"{(score_difference or 0):g} strokes higher than your overall "
            "average in the current data."
        )
    return (
        f"Rounds following {practice_name} practice were similar to your "
        "overall scoring average."
    )


def _associated_rounds(
    practice_sessions: list[PracticeSession],
    user_rounds: list[Round],
    lookback_days: int,
) -> list[Round]:
    associated_by_identifier: dict[int, Round] = {}
    for practice_session in practice_sessions:
        window_end = practice_session.session_date + timedelta(days=lookback_days)
        for user_round in user_rounds:
            if practice_session.session_date < user_round.round_date <= window_end:
                associated_by_identifier[user_round.id] = user_round
    return sorted(
        associated_by_identifier.values(),
        key=lambda user_round: (user_round.round_date, user_round.id),
    )


def get_practice_type_effectiveness(
    db: Session,
    current_user: User,
    lookback_days: int = 14,
    minimum_rounds: int = 2,
) -> PracticeTypeEffectivenessResponse:
    practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .order_by(PracticeSession.session_date, PracticeSession.id)
        .all()
    )
    user_rounds = (
        db.query(Round)
        .filter(Round.user_id == current_user.id)
        .order_by(Round.round_date, Round.id)
        .all()
    )
    sessions_by_type: dict[str, list[PracticeSession]] = defaultdict(list)
    for practice_session in practice_sessions:
        normalized_name = _normalize_practice_type(practice_session.practice_type)
        if normalized_name is not None:
            sessions_by_type[normalized_name].append(practice_session)

    overall_average_score = _average_score(
        [user_round.total_score for user_round in user_rounds]
    )
    results: list[PracticeTypeEffectivenessResult] = []
    # Deduplication is per practice type. A round may intentionally appear in
    # multiple type groups when different practice types precede it.
    for normalized_name, grouped_sessions in sessions_by_type.items():
        associated_round_records = _associated_rounds(
            grouped_sessions, user_rounds, lookback_days
        )
        associated_scores = [
            user_round.total_score for user_round in associated_round_records
        ]
        associated_average = _average_score(associated_scores)
        score_difference = (
            round(associated_average - overall_average_score, 2)
            if associated_average is not None and overall_average_score is not None
            else None
        )
        effectiveness_label = _effectiveness_label(
            len(associated_scores), minimum_rounds, score_difference
        )
        display_name = _display_practice_type(normalized_name)
        results.append(
            PracticeTypeEffectivenessResult(
                practice_type=display_name,
                practice_session_count=len(grouped_sessions),
                associated_round_count=len(associated_scores),
                average_associated_round_score=associated_average,
                best_associated_round_score=(
                    min(associated_scores) if associated_scores else None
                ),
                worst_associated_round_score=(
                    max(associated_scores) if associated_scores else None
                ),
                score_difference=score_difference,
                effectiveness_label=effectiveness_label,
                confidence_label=_confidence_label(
                    len(associated_scores), minimum_rounds
                ),
                observation=_observation(
                    display_name, effectiveness_label, score_difference
                ),
            )
        )

    results.sort(
        key=lambda result: (
            result.effectiveness_label == "insufficient_data",
            result.score_difference is None,
            result.score_difference if result.score_difference is not None else 0.0,
            -result.associated_round_count,
            result.practice_type.casefold(),
        )
    )
    return PracticeTypeEffectivenessResponse(
        total_practice_types=len(results),
        total_practice_sessions_analyzed=sum(
            len(grouped_sessions) for grouped_sessions in sessions_by_type.values()
        ),
        total_rounds_analyzed=len(user_rounds),
        overall_average_score=overall_average_score,
        lookback_days=lookback_days,
        minimum_rounds=minimum_rounds,
        results=results,
    )
