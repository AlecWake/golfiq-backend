import re
from collections import Counter

from sqlalchemy.orm import Session

from app.db.models.golfer_profile import GolferProfile
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.scoring_goal_progress import GoalStatus, ScoringGoalProgressResponse
from app.services.improvement_timeline_service import _trend_label
from app.services.round_analytics_service import _average


RECENT_ROUND_WINDOW = 5
_UNDER_GOAL_PATTERN = re.compile(
    r"^(?:break|shoot\s+under|score\s+below|average\s+under)\s+(\d{2,3})$",
    re.IGNORECASE,
)
_NUMERIC_GOAL_PATTERN = re.compile(r"^(\d{2,3})$")


def parse_scoring_goal(scoring_goal: str | None) -> int | None:
    if scoring_goal is None:
        return None

    normalized_goal = " ".join(scoring_goal.split())
    under_match = _UNDER_GOAL_PATTERN.fullmatch(normalized_goal)
    if under_match is not None:
        threshold = int(under_match.group(1))
        return threshold - 1 if threshold > 1 else None

    numeric_match = _NUMERIC_GOAL_PATTERN.fullmatch(normalized_goal)
    if numeric_match is not None:
        target_score = int(numeric_match.group(1))
        return target_score if target_score > 0 else None

    return None


def _empty_response(
    scoring_goal: str | None,
    goal_status: GoalStatus,
    target_score: int | None,
    observation: str,
) -> ScoringGoalProgressResponse:
    return ScoringGoalProgressResponse(
        scoring_goal=scoring_goal,
        target_score=target_score,
        goal_status=goal_status,
        total_rounds=0,
        recent_rounds_considered=0,
        current_average_score=None,
        recent_average_score=None,
        best_score=None,
        rounds_at_or_below_target=0,
        percentage_at_or_below_target=0.0,
        strokes_from_goal=None,
        trend_label="insufficient_data",
        observation=observation,
    )


def _dominant_holes_played(user_rounds: list[Round]) -> int:
    format_counts = Counter(user_round.holes_played for user_round in user_rounds)
    return max(
        format_counts,
        key=lambda holes_played: (format_counts[holes_played], holes_played),
    )


def _response_without_target(
    scoring_goal: str | None,
    goal_status: GoalStatus,
    observation: str,
    owned_rounds: list[Round],
) -> ScoringGoalProgressResponse:
    if not owned_rounds:
        return _empty_response(scoring_goal, goal_status, None, observation)

    dominant_format = _dominant_holes_played(owned_rounds)
    comparable_rounds = [
        user_round
        for user_round in owned_rounds
        if user_round.holes_played == dominant_format
    ]
    recent_rounds = comparable_rounds[:RECENT_ROUND_WINDOW]
    score_values = [user_round.total_score for user_round in comparable_rounds]
    recent_score_values = [user_round.total_score for user_round in recent_rounds]
    trend_label = (
        _trend_label(recent_rounds[0].total_score, recent_rounds[1].total_score)
        if len(recent_rounds) >= 2
        else "insufficient_data"
    )
    return ScoringGoalProgressResponse(
        scoring_goal=scoring_goal,
        target_score=None,
        goal_status=goal_status,
        total_rounds=len(comparable_rounds),
        recent_rounds_considered=len(recent_rounds),
        current_average_score=_average(score_values),
        recent_average_score=_average(recent_score_values),
        best_score=min(score_values),
        rounds_at_or_below_target=0,
        percentage_at_or_below_target=0.0,
        strokes_from_goal=None,
        trend_label=trend_label,
        observation=observation,
    )


def get_scoring_goal_progress(
    db: Session,
    current_user: User,
) -> ScoringGoalProgressResponse:
    golfer_profile = (
        db.query(GolferProfile)
        .filter(GolferProfile.user_id == current_user.id)
        .first()
    )
    scoring_goal = golfer_profile.scoring_goal if golfer_profile is not None else None
    owned_rounds = (
        db.query(Round)
        .filter(Round.user_id == current_user.id)
        .order_by(Round.round_date.desc(), Round.id.desc())
        .all()
    )

    if scoring_goal is None or not scoring_goal.strip():
        return _response_without_target(
            scoring_goal,
            "no_goal",
            "Add a scoring goal to your golfer profile to track progress.",
            owned_rounds,
        )

    target_score = parse_scoring_goal(scoring_goal)
    if target_score is None:
        return _response_without_target(
            scoring_goal,
            "unrecognized_goal",
            "Your scoring goal could not be converted into a numeric target.",
            owned_rounds,
        )
    if not owned_rounds:
        return _empty_response(
            scoring_goal,
            "insufficient_data",
            target_score,
            "You need more round data before progress can be evaluated.",
        )

    dominant_format = _dominant_holes_played(owned_rounds)
    comparable_rounds = [
        user_round
        for user_round in owned_rounds
        if user_round.holes_played == dominant_format
    ]
    recent_rounds = comparable_rounds[:RECENT_ROUND_WINDOW]
    score_values = [user_round.total_score for user_round in comparable_rounds]
    recent_score_values = [user_round.total_score for user_round in recent_rounds]
    current_average = _average(score_values)
    recent_average = _average(recent_score_values)
    rounds_at_target = sum(score_value <= target_score for score_value in score_values)
    recent_rounds_at_target = sum(
        score_value <= target_score for score_value in recent_score_values
    )
    percentage_at_target = round((rounds_at_target / len(score_values)) * 100, 2)

    if rounds_at_target == 0:
        goal_status = "not_yet_reached"
        observation = (
            f"Your recent average is {recent_average - target_score:.1f} "
            "strokes above your target."
        )
    elif recent_rounds_at_target / len(recent_rounds) >= 0.5:
        goal_status = "consistently_reached"
        observation = "At least half of your recent rounds have met your target."
    else:
        goal_status = "occasionally_reached"
        observation = (
            f"You have reached your target in {rounds_at_target} of "
            f"{len(score_values)} rounds."
        )

    trend_label = (
        _trend_label(recent_rounds[0].total_score, recent_rounds[1].total_score)
        if len(recent_rounds) >= 2
        else "insufficient_data"
    )

    return ScoringGoalProgressResponse(
        scoring_goal=scoring_goal,
        target_score=target_score,
        goal_status=goal_status,
        total_rounds=len(comparable_rounds),
        recent_rounds_considered=len(recent_rounds),
        current_average_score=current_average,
        recent_average_score=recent_average,
        best_score=min(score_values),
        rounds_at_or_below_target=rounds_at_target,
        percentage_at_or_below_target=percentage_at_target,
        strokes_from_goal=round(recent_average - target_score, 2),
        trend_label=trend_label,
        observation=observation,
    )
