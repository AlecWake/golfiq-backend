from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.recommendation import (
    PracticePlanResponse,
    PracticePriorityResponse,
    RecommendationResponse,
)
from app.services.practice_plan_service import get_personalized_practice_plan
from app.services.practice_priority_service import get_practice_priorities
from app.services.recommendation_service import get_user_recommendations


router = APIRouter()


@router.get(
    "/practice-plan",
    response_model=PracticePlanResponse,
    status_code=status.HTTP_200_OK,
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
)
def list_practice_priorities_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_priorities(db, current_user)
