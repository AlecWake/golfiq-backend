"""Shared, side-effect-free helpers for analytics calculations."""

from collections.abc import Sequence


def average_or_zero(values: Sequence[int | float]) -> float:
    """Return a two-decimal average, or zero when no values are available."""
    if not values:
        return 0.0

    return round(sum(values) / len(values), 2)


def score_trend_label(current_score: int, previous_score: int | None) -> str:
    """Describe score movement, where a lower golf score is an improvement."""
    if previous_score is None:
        return "insufficient_data"
    if current_score < previous_score:
        return "improving"
    if current_score > previous_score:
        return "declining"
    return "stable"
