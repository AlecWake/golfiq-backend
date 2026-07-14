from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.round_analytics import RoundAnalyticsSummaryResponse
from app.services.round_analytics_service import get_round_analytics_summary


router = APIRouter()


@router.get(
    "/{round_id}/analytics",
    response_model=RoundAnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a round",
    description="Calculate scoring and performance metrics for an owned round.",
)
def get_round_analytics_summary_endpoint(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_round_analytics_summary(db, current_user, round_id)
