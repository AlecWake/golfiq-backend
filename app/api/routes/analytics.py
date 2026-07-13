from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.improvement_timeline import ImprovementTimelineResponse
from app.schemas.practice_analytics import PracticeAnalyticsSummaryResponse
from app.schemas.practice_effectiveness import PracticeEffectivenessResponse
from app.schemas.practice_round_correlation import PracticeRoundCorrelationResponse
from app.schemas.practice_type_effectiveness import PracticeTypeEffectivenessResponse
from app.schemas.round_analytics import MultiRoundAnalyticsSummaryResponse
from app.schemas.swing_thought_effectiveness import SwingThoughtEffectivenessResult
from app.services.improvement_timeline_service import get_improvement_timeline
from app.services.practice_analytics_service import get_practice_analytics_summary
from app.services.practice_effectiveness_service import get_practice_effectiveness
from app.services.practice_round_correlation_service import (
    get_practice_round_correlation,
)
from app.services.round_analytics_service import get_multi_round_analytics_summary
from app.services.swing_thought_effectiveness_service import (
    get_swing_thought_effectiveness,
)
from app.services.practice_type_effectiveness_service import (
    get_practice_type_effectiveness,
)


router = APIRouter()


@router.get(
    "/practice-types/effectiveness",
    response_model=PracticeTypeEffectivenessResponse,
    status_code=status.HTTP_200_OK,
)
def get_practice_type_effectiveness_endpoint(
    lookback_days: int = Query(default=14, ge=1, le=90),
    minimum_rounds: int = Query(default=2, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_type_effectiveness(
        db, current_user, lookback_days, minimum_rounds
    )


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


@router.get(
    "/practice-effectiveness",
    response_model=PracticeEffectivenessResponse,
    status_code=status.HTTP_200_OK,
)
def get_practice_effectiveness_endpoint(
    lookback_days: int = Query(default=14, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_effectiveness(db, current_user, lookback_days)


@router.get(
    "/swing-thought-effectiveness",
    response_model=list[SwingThoughtEffectivenessResult],
    status_code=status.HTTP_200_OK,
)
def get_swing_thought_effectiveness_endpoint(
    lookback_days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_swing_thought_effectiveness(db, current_user, lookback_days)


@router.get(
    "/improvement-timeline",
    response_model=ImprovementTimelineResponse,
    status_code=status.HTTP_200_OK,
)
def get_improvement_timeline_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_improvement_timeline(db, current_user)
