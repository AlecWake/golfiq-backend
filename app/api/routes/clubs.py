from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.club import ClubCreateRequest, ClubResponse, ClubUpdateRequest
from app.services.club_service import (
    create_club,
    delete_club,
    get_user_club,
    get_user_clubs,
    update_club,
)


router = APIRouter()


@router.post(
    "",
    response_model=ClubResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_club_endpoint(
    club_data: ClubCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_club(db, current_user, club_data)


@router.get(
    "",
    response_model=list[ClubResponse],
    status_code=status.HTTP_200_OK,
)
def list_clubs_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_clubs(db, current_user)


@router.get(
    "/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
)
def get_club_endpoint(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_club(db, current_user, club_id)


@router.put(
    "/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
)
def update_club_endpoint(
    club_id: int,
    club_data: ClubUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_club(db, current_user, club_id, club_data)


@router.delete(
    "/{club_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_club_endpoint(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_club(db, current_user, club_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)