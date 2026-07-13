from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round
from app.db.models.user import User
from app.schemas.activity import (
    ActivityFeedResponse,
    ActivityItemResponse,
    ActivityType,
    PracticeActivityMetadata,
    RoundActivityMetadata,
)


def _map_round_activity(round_record: Round) -> ActivityItemResponse:
    return ActivityItemResponse(
        activity_type="round",
        activity_id=round_record.id,
        activity_date=round_record.round_date,
        title=round_record.course_name,
        summary=f"{round_record.holes_played}-hole round: {round_record.total_score}",
        created_at=round_record.created_at,
        metadata=RoundActivityMetadata(
            course_name=round_record.course_name,
            tee_box=round_record.tee_box,
            holes_played=round_record.holes_played,
            total_score=round_record.total_score,
        ),
    )


def _format_practice_summary(practice_session_record: PracticeSession) -> str:
    practice_label = practice_session_record.practice_type
    if practice_session_record.duration_minutes is None:
        summary = f"{practice_label.capitalize()} practice"
    else:
        summary = (
            f"{practice_session_record.duration_minutes}-minute "
            f"{practice_label} session"
        )

    if practice_session_record.overall_rating is not None:
        summary += f" rated {practice_session_record.overall_rating}/10"

    return summary


def _map_practice_activity(
    practice_session_record: PracticeSession,
) -> ActivityItemResponse:
    return ActivityItemResponse(
        activity_type="practice",
        activity_id=practice_session_record.id,
        activity_date=practice_session_record.session_date,
        title=practice_session_record.practice_type,
        summary=_format_practice_summary(practice_session_record),
        created_at=practice_session_record.created_at,
        metadata=PracticeActivityMetadata(
            practice_type=practice_session_record.practice_type,
            duration_minutes=practice_session_record.duration_minutes,
            overall_rating=practice_session_record.overall_rating,
        ),
    )


def get_activity_feed(
    db: Session,
    current_user: User,
    activity_type: ActivityType,
    limit: int,
    offset: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> ActivityFeedResponse:
    activity_items: list[ActivityItemResponse] = []

    if activity_type in (ActivityType.ALL, ActivityType.ROUND):
        round_query = select(Round).where(Round.user_id == current_user.id)
        if date_from is not None:
            round_query = round_query.where(Round.round_date >= date_from)
        if date_to is not None:
            round_query = round_query.where(Round.round_date <= date_to)
        round_records = db.scalars(round_query).all()
        activity_items.extend(_map_round_activity(record) for record in round_records)

    if activity_type in (ActivityType.ALL, ActivityType.PRACTICE):
        practice_query = select(PracticeSession).where(
            PracticeSession.user_id == current_user.id
        )
        if date_from is not None:
            practice_query = practice_query.where(
                PracticeSession.session_date >= date_from
            )
        if date_to is not None:
            practice_query = practice_query.where(
                PracticeSession.session_date <= date_to
            )
        practice_records = db.scalars(practice_query).all()
        activity_items.extend(
            _map_practice_activity(record) for record in practice_records
        )

    # Pagination is intentionally performed after combining both small resource sets.
    activity_items.sort(
        key=lambda item: (
            item.activity_date,
            item.created_at,
            item.activity_type,
            item.activity_id,
        ),
        reverse=True,
    )
    total_items = len(activity_items)
    page_items = activity_items[offset : offset + limit]

    return ActivityFeedResponse(
        total=total_items,
        limit=limit,
        offset=offset,
        has_more=offset + len(page_items) < total_items,
        items=page_items,
    )
