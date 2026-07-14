from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.recommendation import (
    PracticePlanResponse,
    PracticePriorityResponse,
    RecommendationResponse,
    WeeklyPracticeScheduleResponse,
)
from app.services.practice_plan_service import get_personalized_practice_plan
from app.services.practice_priority_service import get_practice_priorities
from app.services.recommendation_service import get_user_recommendations
from app.services.weekly_practice_schedule_service import (
    get_weekly_practice_schedule,
)


router = APIRouter()


@router.get(
    "/weekly-practice-schedule",
    response_model=WeeklyPracticeScheduleResponse,
    status_code=status.HTTP_200_OK,
    summary="Build a weekly practice schedule",
    description="Distribute personalized practice focus across the requested week.",
)
def get_weekly_practice_schedule_endpoint(
    available_days: int = Query(default=3, ge=1, le=7),
    minutes_per_day: int = Query(default=60, ge=15, le=180),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_weekly_practice_schedule(
        db,
        current_user,
        available_days,
        minutes_per_day,
    )


@router.get(
    "/practice-plan",
    response_model=PracticePlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Build a practice plan",
    description="Return an ordered practice session tailored to recent performance.",
)
def get_practice_plan_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_personalized_practice_plan(db, current_user)


@router.get(
    "",
    response_model=list[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="List recommendations",
    description="Return actionable recommendations based on the golfer's data.",
)
def list_recommendations_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_recommendations(db, current_user)


@router.get(
    "/practice-priorities",
    response_model=list[PracticePriorityResponse],
    status_code=status.HTTP_200_OK,
    summary="List practice priorities",
    description="Rank the golfer's most important practice focus areas.",
)
def list_practice_priorities_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_priorities(db, current_user)
