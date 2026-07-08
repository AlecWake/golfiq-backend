from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import get_user_recommendations


router = APIRouter()


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
