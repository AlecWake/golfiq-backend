from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.round import RoundCreateRequest, RoundResponse, RoundUpdateRequest
from app.services.round_service import (
    create_round,
    delete_round,
    get_user_round,
    get_user_rounds,
    update_round,
)


router = APIRouter()


@router.post(
    "",
    response_model=RoundResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_round_endpoint(
    round_data: RoundCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_round(db, current_user, round_data)


@router.get(
    "",
    response_model=list[RoundResponse],
    status_code=status.HTTP_200_OK,
)
def list_rounds_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_rounds(db, current_user)


@router.get(
    "/{round_id}",
    response_model=RoundResponse,
    status_code=status.HTTP_200_OK,
)
def get_round_endpoint(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_round(db, current_user, round_id)


@router.put(
    "/{round_id}",
    response_model=RoundResponse,
    status_code=status.HTTP_200_OK,
)
def update_round_endpoint(
    round_id: int,
    round_data: RoundUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_round(db, current_user, round_id, round_data)


@router.delete(
    "/{round_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_round_endpoint(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_round(db, current_user, round_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
