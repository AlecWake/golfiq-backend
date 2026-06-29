from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.practice_session import (
    PracticeSessionCreateRequest,
    PracticeSessionResponse,
    PracticeSessionUpdateRequest,
)
from app.schemas.swing_thought import SwingThoughtResponse
from app.services.practice_session_service import (
    create_practice_session,
    delete_practice_session,
    get_practice_session_swing_thoughts,
    get_user_practice_session,
    get_user_practice_sessions,
    link_swing_thought_to_practice_session,
    unlink_swing_thought_from_practice_session,
    update_practice_session,
)


router = APIRouter()


@router.post(
    "",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_practice_session_endpoint(
    practice_session_data: PracticeSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_practice_session(db, current_user, practice_session_data)


@router.get(
    "",
    response_model=list[PracticeSessionResponse],
    status_code=status.HTTP_200_OK,
)
def list_practice_sessions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_practice_sessions(db, current_user)


@router.get(
    "/{practice_session_id}",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_200_OK,
)
def get_practice_session_endpoint(
    practice_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_practice_session(db, current_user, practice_session_id)


@router.post(
    "/{practice_session_id}/swing-thoughts/{swing_thought_id}",
    response_model=SwingThoughtResponse,
    status_code=status.HTTP_201_CREATED,
)
def link_swing_thought_to_practice_session_endpoint(
    practice_session_id: int,
    swing_thought_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return link_swing_thought_to_practice_session(
        db,
        current_user,
        practice_session_id,
        swing_thought_id,
    )


@router.delete(
    "/{practice_session_id}/swing-thoughts/{swing_thought_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unlink_swing_thought_from_practice_session_endpoint(
    practice_session_id: int,
    swing_thought_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unlink_swing_thought_from_practice_session(
        db,
        current_user,
        practice_session_id,
        swing_thought_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{practice_session_id}/swing-thoughts",
    response_model=list[SwingThoughtResponse],
    status_code=status.HTTP_200_OK,
)
def list_practice_session_swing_thoughts_endpoint(
    practice_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_practice_session_swing_thoughts(
        db,
        current_user,
        practice_session_id,
    )


@router.put(
    "/{practice_session_id}",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_200_OK,
)
def update_practice_session_endpoint(
    practice_session_id: int,
    practice_session_data: PracticeSessionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_practice_session(
        db,
        current_user,
        practice_session_id,
        practice_session_data,
    )


@router.delete(
    "/{practice_session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_practice_session_endpoint(
    practice_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_practice_session(db, current_user, practice_session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
