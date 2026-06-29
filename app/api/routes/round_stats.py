from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.round_stat import (
    RoundStatCreateRequest,
    RoundStatResponse,
    RoundStatUpdateRequest,
)
from app.services.round_stat_service import (
    create_round_stat,
    delete_round_stat,
    get_round_stat,
    update_round_stat,
)


router = APIRouter()


@router.post(
    "/{round_id}/stats",
    response_model=RoundStatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_round_stat_endpoint(
    round_id: int,
    stat_data: RoundStatCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_round_stat(db, current_user, round_id, stat_data)


@router.get(
    "/{round_id}/stats",
    response_model=RoundStatResponse,
    status_code=status.HTTP_200_OK,
)
def get_round_stat_endpoint(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_round_stat(db, current_user, round_id)


@router.put(
    "/{round_id}/stats",
    response_model=RoundStatResponse,
    status_code=status.HTTP_200_OK,
)
def update_round_stat_endpoint(
    round_id: int,
    stat_data: RoundStatUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_round_stat(db, current_user, round_id, stat_data)


@router.delete(
    "/{round_id}/stats",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_round_stat_endpoint(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_round_stat(db, current_user, round_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
