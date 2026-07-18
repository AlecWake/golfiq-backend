from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session, selectinload

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.swing_thought import SwingThought
from app.db.models.user import User
from app.schemas.recommendation import PracticePriorityResponse
from app.services.analytics_utils import average_or_zero
from app.services.round_analytics_service import (
    _fairway_percentage_for_round,
    _gir_percentage_for_round,
    _stat_values_for_round,
)
from app.services.profile_personalization_service import (
    ProfileContext,
    get_profile_context,
)


RECENT_ACTIVITY_DAYS = 30
PRIORITY_LEVEL_SCORES = {"High": 3, "Medium": 2, "Low": 1}
CATEGORY_ORDER = {
    "Penalties": 1,
    "Putting": 2,
    "Iron Play": 3,
    "Accuracy": 4,
    "Consistency": 5,
    "Practice Frequency": 6,
    "Swing Thoughts": 7,
    "Ball Striking": 8,
    "Driving": 9,
}


@dataclass(frozen=True)
class PracticePriorityCandidate:
    category: str
    priority_level: str
    title: str
    explanation: str
    supporting_metric: str
    suggested_focus: str
    severity_score: float


def _latest_activity_date(
    practice_sessions: list[PracticeSession],
    user_rounds: list[Round],
) -> date | None:
    activity_dates = [
        practice_session.session_date for practice_session in practice_sessions
    ]
    activity_dates.extend(user_round.round_date for user_round in user_rounds)

    if not activity_dates:
        return None

    return max(activity_dates)


def _candidate(
    category: str,
    priority_level: str,
    title: str,
    explanation: str,
    supporting_metric: str,
    suggested_focus: str,
    severity_score: float = 0.0,
) -> PracticePriorityCandidate:
    return PracticePriorityCandidate(
        category=category,
        priority_level=priority_level,
        title=title,
        explanation=explanation,
        supporting_metric=supporting_metric,
        suggested_focus=suggested_focus,
        severity_score=severity_score,
    )


def _add_practice_frequency_priority(
    priorities: list[PracticePriorityCandidate],
    practice_sessions: list[PracticeSession],
    user_rounds: list[Round],
) -> None:
    if not practice_sessions:
        priorities.append(
            _candidate(
                "Practice Frequency",
                "High",
                "Start a weekly practice rhythm",
                "You have not logged any practice sessions yet, so building a repeatable practice habit is the best first step.",
                "Practice sessions logged: 0",
                "Schedule one focused practice session this week and log what you worked on.",
                1.0,
            )
        )
        return

    latest_activity = _latest_activity_date(practice_sessions, user_rounds)
    latest_session_date = max(
        practice_session.session_date for practice_session in practice_sessions
    )

    if (
        latest_activity is not None
        and (latest_activity - latest_session_date).days > RECENT_ACTIVITY_DAYS
    ):
        days_since_practice = (latest_activity - latest_session_date).days
        priorities.append(
            _candidate(
                "Practice Frequency",
                "High",
                "Refresh your practice routine",
                "Your recent golf activity is not being supported by recent logged practice.",
                f"Days since last practice: {days_since_practice}",
                "Add a short, focused range or putting session before your next round.",
                min(days_since_practice / RECENT_ACTIVITY_DAYS, 3.0),
            )
        )

    if len(practice_sessions) < 3:
        priorities.append(
            _candidate(
                "Practice Frequency",
                "Medium",
                "Build more practice history",
                "A few more logged sessions will make your practice priorities more reliable.",
                f"Practice sessions logged: {len(practice_sessions)}",
                "Log at least three practice sessions with a clear focus area.",
                0.5,
            )
        )


def _add_swing_thought_priority(
    priorities: list[PracticePriorityCandidate],
    active_swing_thoughts_count: int,
) -> None:
    if active_swing_thoughts_count > 0:
        return

    priorities.append(
        _candidate(
            "Swing Thoughts",
            "Medium",
            "Create one active swing thought",
            "You do not have an active swing thought to connect practice work with on-course execution.",
            "Active swing thoughts: 0",
            "Pick one simple cue for your next practice session, such as tempo, balance, or finish position.",
            1.0,
        )
    )


def _add_round_metric_priorities(
    priorities: list[PracticePriorityCandidate],
    user_rounds: list[Round],
) -> None:
    if not user_rounds:
        priorities.append(
            _candidate(
                "Ball Striking",
                "Low",
                "Create a baseline with your next round",
                "You do not have round data yet, so a simple full-swing baseline will help future priorities.",
                "Rounds logged: 0",
                "After your next round, log score, putts, penalties, fairways, and greens when available.",
                0.1,
            )
        )
        return

    scores = [user_round.total_score for user_round in user_rounds]
    putt_totals: list[int] = []
    penalty_totals: list[int] = []
    fairway_percentages: list[float] = []
    gir_percentages: list[float] = []

    for user_round in user_rounds:
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

    average_putts = average_or_zero(putt_totals)
    average_penalties = average_or_zero(penalty_totals)
    average_fairway_percentage = average_or_zero(fairway_percentages)
    average_gir_percentage = average_or_zero(gir_percentages)

    if putt_totals and average_putts > 36:
        priorities.append(
            _candidate(
                "Putting",
                "High",
                "Prioritize putting efficiency",
                "Your average putts are high enough that gains on the greens can quickly lower scores.",
                f"Average putts: {average_putts} per round",
                "Spend extra time on distance control, three-to-six foot putts, and lag putting games.",
                average_putts - 36,
            )
        )
    elif putt_totals and average_putts >= 33:
        priorities.append(
            _candidate(
                "Putting",
                "Medium",
                "Sharpen putting consistency",
                "Your putting numbers suggest room to save strokes with more consistent speed and start line.",
                f"Average putts: {average_putts} per round",
                "Practice speed control ladders and short putt start-line drills.",
                average_putts - 32,
            )
        )

    if gir_percentages and average_gir_percentage < 35:
        priorities.append(
            _candidate(
                "Iron Play",
                "High",
                "Improve approach shot quality",
                "Your greens in regulation rate is low, which points to approach shots as a high-value practice area.",
                f"Average GIR: {average_gir_percentage}%",
                "Work on stock iron distances, wedge control, and choosing safer approach targets.",
                35 - average_gir_percentage,
            )
        )
    elif gir_percentages and average_gir_percentage < 50:
        priorities.append(
            _candidate(
                "Iron Play",
                "Medium",
                "Raise your GIR baseline",
                "Your approach play is close enough that a modest GIR improvement could show up in scoring.",
                f"Average GIR: {average_gir_percentage}%",
                "Practice mid-iron contact and wedge distance windows.",
                50 - average_gir_percentage,
            )
        )

    if penalty_totals and average_penalties >= 2:
        priorities.append(
            _candidate(
                "Penalties",
                "High",
                "Reduce avoidable penalty strokes",
                "Penalty strokes are adding enough score pressure to deserve immediate attention.",
                f"Average penalties: {average_penalties} per round",
                "Choose conservative targets around trouble and practice a reliable fairway-finder shot.",
                average_penalties,
            )
        )
    elif penalty_totals and average_penalties >= 1:
        priorities.append(
            _candidate(
                "Penalties",
                "Medium",
                "Keep more balls in play",
                "A small penalty reduction can protect your score on difficult holes.",
                f"Average penalties: {average_penalties} per round",
                "Review where penalties happen and rehearse safer club choices for those holes.",
                average_penalties,
            )
        )

    if fairway_percentages and average_fairway_percentage < 35:
        priorities.append(
            _candidate(
                "Accuracy",
                "High",
                "Stabilize tee shot accuracy",
                "Your fairway rate is low, so improving start direction and shot pattern can reduce pressure on approach shots.",
                f"Average fairways hit: {average_fairway_percentage}%",
                "Practice controlled tee shots with a specific target and a predictable curve.",
                35 - average_fairway_percentage,
            )
        )
    elif fairway_percentages and average_fairway_percentage < 50:
        priorities.append(
            _candidate(
                "Accuracy",
                "Medium",
                "Tighten your tee shot pattern",
                "Your fairway rate suggests accuracy work can make rounds easier to manage.",
                f"Average fairways hit: {average_fairway_percentage}%",
                "Use alignment gates and commit to one stock tee shot shape.",
                50 - average_fairway_percentage,
            )
        )

    if len(scores) >= 3:
        score_range = max(scores) - min(scores)
        if score_range >= 20:
            priorities.append(
                _candidate(
                    "Consistency",
                    "High",
                    "Narrow your scoring range",
                    "Your scores vary significantly from round to round, which points to consistency as a major opportunity.",
                    f"Score range: {score_range} strokes",
                    "Compare notes from your best and hardest rounds, then practice the patterns that break down most often.",
                    score_range / 10,
                )
            )
        elif score_range >= 15:
            priorities.append(
                _candidate(
                    "Consistency",
                    "Medium",
                    "Build more repeatable scoring",
                    "Your scores vary enough that steadier decision-making and execution could lower your average.",
                    f"Score range: {score_range} strokes",
                    "Track pre-round goals and post-round misses to find recurring scoring leaks.",
                    score_range / 10,
                )
            )

    if not putt_totals and not penalty_totals and not fairway_percentages and not gir_percentages:
        priorities.append(
            _candidate(
                "Ball Striking",
                "Low",
                "Add detail to future rounds",
                "Your rounds do not include enough supporting stats yet, so future priorities will improve as you log more detail.",
                f"Rounds logged without analytics: {len(user_rounds)}",
                "Log putts, penalties, fairways, and greens for the next round when possible.",
                0.2,
            )
        )


def _rank_priorities(
    priorities: list[PracticePriorityCandidate],
    profile_context: ProfileContext,
) -> list[PracticePriorityResponse]:
    ordered_priorities = sorted(
        priorities,
        key=lambda priority: (
            -PRIORITY_LEVEL_SCORES[priority.priority_level],
            -priority.severity_score,
            -profile_context.category_tie_breaker(priority.category),
            CATEGORY_ORDER[priority.category],
            priority.title,
        ),
    )

    return [
        PracticePriorityResponse(
            priority_rank=index + 1,
            category=priority.category,
            priority_level=priority.priority_level,
            title=priority.title,
            explanation=priority.explanation,
            supporting_metric=priority.supporting_metric,
            suggested_focus=priority.suggested_focus,
        )
        for index, priority in enumerate(ordered_priorities)
    ]


def get_practice_priorities(
    db: Session,
    current_user: User,
) -> list[PracticePriorityResponse]:
    practice_sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .all()
    )
    user_rounds = (
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
    priorities: list[PracticePriorityCandidate] = []
    profile_context = get_profile_context(db, current_user)

    _add_practice_frequency_priority(priorities, practice_sessions, user_rounds)
    _add_swing_thought_priority(priorities, active_swing_thoughts_count)
    _add_round_metric_priorities(priorities, user_rounds)
    _add_profile_priority(priorities, profile_context, user_rounds)

    if not priorities:
        priorities.append(
            _candidate(
                "Consistency",
                "Low",
                "Keep reinforcing what is working",
                "Your logged data does not show an urgent weakness, so maintenance and steady tracking are the right priorities.",
                "No high-priority gaps detected",
                "Continue balanced practice and keep logging round and practice details.",
                0.0,
            )
        )

    return _rank_priorities(_deduplicate_categories(priorities), profile_context)


def _add_profile_priority(
    priorities: list[PracticePriorityCandidate],
    profile_context: ProfileContext,
    user_rounds: list[Round],
) -> None:
    # Strong round evidence wins. Profile context can add a low-priority focus when
    # history is sparse, and participates only after severity when ordering ties.
    if len(user_rounds) >= 3 or profile_context.fallback_focus is None:
        return
    category, focus_name, suggested_focus = profile_context.fallback_focus
    profile_metric = (
        f"Profile dominant miss: {profile_context.dominant_miss}"
        if profile_context.dominant_miss is not None
        else "Golfer profile context"
    )
    profile_reason = (
        f"Your profile notes a {profile_context.dominant_miss} miss"
        if profile_context.dominant_miss is not None
        else "Your experience and handicap profile"
    )
    priorities.append(
        _candidate(
            category,
            "Low",
            f"Build a {focus_name.lower()} baseline",
            f"{profile_reason} makes this a useful secondary focus while more round data is collected."
            f"{profile_context.goal_suffix()}",
            profile_metric,
            f"Use simple target-based practice for {suggested_focus}.",
            0.15,
        )
    )


def _deduplicate_categories(
    priorities: list[PracticePriorityCandidate],
) -> list[PracticePriorityCandidate]:
    best_by_category: dict[str, PracticePriorityCandidate] = {}
    for practice_priority in priorities:
        existing_priority = best_by_category.get(practice_priority.category)
        if existing_priority is None or (
            PRIORITY_LEVEL_SCORES[practice_priority.priority_level],
            practice_priority.severity_score,
        ) > (
            PRIORITY_LEVEL_SCORES[existing_priority.priority_level],
            existing_priority.severity_score,
        ):
            best_by_category[practice_priority.category] = practice_priority
    return list(best_by_category.values())
