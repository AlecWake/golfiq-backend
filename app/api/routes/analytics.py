from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.practice_analytics import PracticeAnalyticsSummaryResponse
from app.schemas.practice_round_correlation import PracticeRoundCorrelationResponse
from app.schemas.round_analytics import MultiRoundAnalyticsSummaryResponse
from app.services.practice_analytics_service import get_practice_analytics_summary
from app.services.practice_round_correlation_service import (
    get_practice_round_correlation,
)
from app.services.round_analytics_service import get_multi_round_analytics_summary


router = APIRouter()


@router.get(
    "/rounds/summary",
    response_model=MultiRoundAnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_multi_round_analytics_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_multi_round_analytics_summary(db, current_user)


@router.get(
    "/practice/summary",
    response_model=PracticeAnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_practice_analytics_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_analytics_summary(db, current_user)


@router.get(
    "/practice-round-correlation",
    response_model=PracticeRoundCorrelationResponse,
    status_code=status.HTTP_200_OK,
)
def get_practice_round_correlation_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_round_correlation(db, current_user)
