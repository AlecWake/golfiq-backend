from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.user import User
from app.schemas.recommendation import (
    PracticePlanItemResponse,
    WeeklyPracticeScheduleResponse,
    WeeklyScheduleEntryResponse,
    WeeklyScheduleFocusItemResponse,
)
from app.services.practice_plan_service import get_personalized_practice_plan


MINIMUM_BLOCK_MINUTES = 5
BEGINNER_OVERALL_FOCUS = "Build a balanced practice foundation"


def _find_available_day(
    day_minutes: list[int],
    starting_day_index: int,
    minutes_per_day: int,
) -> int | None:
    for offset in range(len(day_minutes)):
        day_index = (starting_day_index + offset) % len(day_minutes)
        if minutes_per_day - day_minutes[day_index] >= MINIMUM_BLOCK_MINUTES:
            return day_index
    return None


def _allocate_items(
    practice_items: list[PracticePlanItemResponse],
    available_days: int,
    minutes_per_day: int,
) -> list[WeeklyScheduleEntryResponse]:
    day_items: list[list[WeeklyScheduleFocusItemResponse]] = [
        [] for _ in range(available_days)
    ]
    day_minutes = [0 for _ in range(available_days)]
    next_day_index = 0

    for practice_item in practice_items:
        day_index = _find_available_day(
            day_minutes,
            next_day_index,
            minutes_per_day,
        )
        if day_index is None:
            break

        remaining_day_minutes = minutes_per_day - day_minutes[day_index]
        allocated_minutes = min(
            practice_item.recommended_minutes,
            remaining_day_minutes,
        )
        if allocated_minutes < MINIMUM_BLOCK_MINUTES:
            continue

        day_items[day_index].append(
            WeeklyScheduleFocusItemResponse(
                order=practice_item.order,
                category=practice_item.category,
                title=practice_item.title,
                recommended_minutes=allocated_minutes,
                reason=practice_item.reason,
                priority=practice_item.priority,
            )
        )
        day_minutes[day_index] += allocated_minutes
        next_day_index = (day_index + 1) % available_days

    return [
        WeeklyScheduleEntryResponse(
            day_number=day_index + 1,
            session_title=f"Practice Day {day_index + 1}",
            total_minutes=day_minutes[day_index],
            focus_items=focus_items,
        )
        for day_index, focus_items in enumerate(day_items)
        if focus_items
    ]


def get_weekly_practice_schedule(
    db: Session,
    current_user: User,
    available_days: int,
    minutes_per_day: int,
) -> WeeklyPracticeScheduleResponse:
    practice_plan = get_personalized_practice_plan(db, current_user)
    schedule = _allocate_items(
        practice_plan.practice_items,
        available_days,
        minutes_per_day,
    )

    if practice_plan.practice_items:
        overall_focus = practice_plan.overall_focus
        confidence = practice_plan.confidence
    else:
        overall_focus = BEGINNER_OVERALL_FOCUS
        confidence = "Low"

    return WeeklyPracticeScheduleResponse(
        generated_at=datetime.now(timezone.utc),
        available_days=available_days,
        minutes_per_day=minutes_per_day,
        total_weekly_minutes=available_days * minutes_per_day,
        overall_focus=overall_focus,
        confidence=confidence,
        schedule=schedule,
    )
