from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.golfer_profile import (
    GolferProfileResponse,
    GolferProfileUpdateRequest,
)
from app.services.golfer_profile_service import (
    get_current_user_profile,
    update_current_user_profile,
)


router = APIRouter()


@router.get(
    "/me/profile",
    response_model=GolferProfileResponse,
    status_code=status.HTTP_200_OK,
)
def get_current_user_profile_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_current_user_profile(db, current_user)


@router.put(
    "/me/profile",
    response_model=GolferProfileResponse,
    status_code=status.HTTP_200_OK,
)
def update_current_user_profile_endpoint(
    profile_data: GolferProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_current_user_profile(db, current_user, profile_data)
