from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.hole_score import (
    HoleScoreCreateRequest,
    HoleScoreResponse,
    HoleScoreUpdateRequest,
)
from app.services.hole_score_service import (
    create_hole_score,
    delete_hole_score,
    get_round_hole_score,
    get_round_hole_scores,
    update_hole_score,
)


router = APIRouter()


@router.post(
    "/{round_id}/hole-scores",
    response_model=HoleScoreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hole_score_endpoint(
    round_id: int,
    hole_score_data: HoleScoreCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_hole_score(db, current_user, round_id, hole_score_data)


@router.get(
    "/{round_id}/hole-scores",
    response_model=list[HoleScoreResponse],
    status_code=status.HTTP_200_OK,
)
def list_hole_scores_endpoint(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_round_hole_scores(db, current_user, round_id)


@router.get(
    "/{round_id}/hole-scores/{hole_score_id}",
    response_model=HoleScoreResponse,
    status_code=status.HTTP_200_OK,
)
def get_hole_score_endpoint(
    round_id: int,
    hole_score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_round_hole_score(db, current_user, round_id, hole_score_id)


@router.put(
    "/{round_id}/hole-scores/{hole_score_id}",
    response_model=HoleScoreResponse,
    status_code=status.HTTP_200_OK,
)
def update_hole_score_endpoint(
    round_id: int,
    hole_score_id: int,
    hole_score_data: HoleScoreUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_hole_score(
        db,
        current_user,
        round_id,
        hole_score_id,
        hole_score_data,
    )


@router.delete(
    "/{round_id}/hole-scores/{hole_score_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_hole_score_endpoint(
    round_id: int,
    hole_score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_hole_score(db, current_user, round_id, hole_score_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
