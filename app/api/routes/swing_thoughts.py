from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.swing_thought import (
    SwingThoughtCreateRequest,
    SwingThoughtResponse,
    SwingThoughtUpdateRequest,
)
from app.services.swing_thought_service import (
    create_swing_thought,
    delete_swing_thought,
    get_user_swing_thought,
    get_user_swing_thoughts,
    update_swing_thought,
)


router = APIRouter()


@router.post(
    "",
    response_model=SwingThoughtResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a swing thought",
    description="Save a reusable swing cue for the authenticated golfer.",
)
def create_swing_thought_endpoint(
    swing_thought_data: SwingThoughtCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_swing_thought(db, current_user, swing_thought_data)


@router.get(
    "",
    response_model=list[SwingThoughtResponse],
    status_code=status.HTTP_200_OK,
    summary="List swing thoughts",
    description="Return the authenticated golfer's saved swing thoughts.",
)
def list_swing_thoughts_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_swing_thoughts(db, current_user)


@router.get(
    "/{swing_thought_id}",
    response_model=SwingThoughtResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a swing thought",
    description="Return one swing thought owned by the authenticated golfer.",
)
def get_swing_thought_endpoint(
    swing_thought_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_swing_thought(db, current_user, swing_thought_id)


@router.put(
    "/{swing_thought_id}",
    response_model=SwingThoughtResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a swing thought",
    description="Replace editable details for an owned swing thought.",
)
def update_swing_thought_endpoint(
    swing_thought_id: int,
    swing_thought_data: SwingThoughtUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_swing_thought(
        db,
        current_user,
        swing_thought_id,
        swing_thought_data,
    )


@router.delete(
    "/{swing_thought_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a swing thought",
    description="Remove a swing thought owned by the authenticated golfer.",
)
def delete_swing_thought_endpoint(
    swing_thought_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_swing_thought(db, current_user, swing_thought_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
