from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.recommendation import (
    PracticePlanConfidence,
    PracticePlanItemResponse,
    PracticePlanResponse,
    PracticePriorityResponse,
)
from app.services.practice_priority_service import get_practice_priorities


MAXIMUM_PLAN_ITEMS = 6
MINIMUM_PLAN_ITEMS = 3
RECOMMENDED_MINUTES = {"High": 25, "Medium": 20, "Low": 15}


def _confidence_for_history(
    practice_session_count: int,
    round_count: int,
) -> PracticePlanConfidence:
    history_count = practice_session_count + round_count
    if history_count >= 6 and round_count >= 3:
        return "High"
    if history_count >= 3 and round_count >= 1:
        return "Moderate"
    return "Low"


def _foundation_priorities() -> list[PracticePriorityResponse]:
    return [
        PracticePriorityResponse(
            priority_rank=1,
            category="Putting",
            priority_level="Low",
            title="Build a reliable putting routine",
            explanation="A simple putting routine develops distance control and confidence while more playing data is collected.",
            supporting_metric="Foundation plan",
            suggested_focus="Practice short putts and lag putting with a consistent pre-putt routine.",
        ),
        PracticePriorityResponse(
            priority_rank=2,
            category="Iron Play",
            priority_level="Low",
            title="Develop consistent contact",
            explanation="Balanced contact practice creates a useful baseline before specific weaknesses are clear.",
            supporting_metric="Foundation plan",
            suggested_focus="Hit controlled half and three-quarter iron shots to a defined target.",
        ),
        PracticePriorityResponse(
            priority_rank=3,
            category="Accuracy",
            priority_level="Low",
            title="Finish with target practice",
            explanation="Target-focused practice helps transfer a repeatable shot pattern to the course.",
            supporting_metric="Foundation plan",
            suggested_focus="Choose a target and rehearse a dependable tee shot shape.",
        ),
    ]


def _ensure_minimum_items(
    priorities: list[PracticePriorityResponse],
) -> list[PracticePriorityResponse]:
    selected_priorities = priorities[:MAXIMUM_PLAN_ITEMS]
    existing_categories = {priority.category for priority in selected_priorities}

    for foundation_priority in _foundation_priorities():
        if len(selected_priorities) >= MINIMUM_PLAN_ITEMS:
            break
        if foundation_priority.category not in existing_categories:
            selected_priorities.append(foundation_priority)
            existing_categories.add(foundation_priority.category)

    return selected_priorities


def get_personalized_practice_plan(
    db: Session,
    current_user: User,
) -> PracticePlanResponse:
    priorities = _ensure_minimum_items(get_practice_priorities(db, current_user))
    practice_session_count = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == current_user.id)
        .count()
    )
    round_count = (
        db.query(Round)
        .filter(Round.user_id == current_user.id)
        .count()
    )

    practice_items = [
        PracticePlanItemResponse(
            order=item_order,
            category=priority.category,
            title=priority.title,
            reason=priority.explanation,
            recommended_minutes=RECOMMENDED_MINUTES[priority.priority_level],
            supporting_metric=priority.supporting_metric,
            priority=priority.priority_level,
        )
        for item_order, priority in enumerate(priorities, start=1)
    ]

    return PracticePlanResponse(
        generated_at=datetime.now(timezone.utc),
        overall_focus=practice_items[0].category,
        confidence=_confidence_for_history(practice_session_count, round_count),
        estimated_session_length_minutes=sum(
            practice_item.recommended_minutes for practice_item in practice_items
        ),
        practice_items=practice_items,
    )
